import os, json, boto3, base64
from datetime import datetime
from decimal import Decimal
from kubernetes import client
from botocore.signers import RequestSigner

dynamodb = boto3.resource('dynamodb')
approvals_table = dynamodb.Table(os.environ.get('APPROVALS_TABLE', 'telco-buddy-approvals'))

def get_k8s_client():
    region = os.environ.get('AWS_REGION', 'us-east-1')
    cluster_name = os.environ.get('CLUSTER_NAME', 'telco-buddy-v2-5g-cluster')
    role_arn = os.environ.get('K8S_ROLE_ARN')

    if role_arn:
        sts = boto3.client('sts')
        creds = sts.assume_role(RoleArn=role_arn, RoleSessionName='approvals')['Credentials']
        session = boto3.Session(
            aws_access_key_id=creds['AccessKeyId'],
            aws_secret_access_key=creds['SecretAccessKey'],
            aws_session_token=creds['SessionToken'])
        eks = session.client('eks', region_name=region)
        # Generate token using assumed role credentials
        sts_for_token = session.client('sts', region_name=region)
    else:
        eks = boto3.client('eks', region_name=region)
        sts_for_token = boto3.client('sts', region_name=region)

    cluster = eks.describe_cluster(name=cluster_name)['cluster']

    signer = RequestSigner(sts_for_token.meta.service_model.service_id, region, 'sts', 'v4',
        sts_for_token._request_signer._credentials, sts_for_token.meta.events)
    params = {'method': 'GET', 'url': f'https://sts.{region}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15',
        'body': {}, 'headers': {'x-k8s-aws-id': cluster_name}, 'context': {}}
    signed_url = signer.generate_presigned_url(params, region_name=region, expires_in=60, operation_name='')
    token = 'k8s-aws-v1.' + base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8').rstrip('=')

    config = client.Configuration()
    config.host = cluster['endpoint']
    config.verify_ssl = True
    config.ssl_ca_cert = '/tmp/ca.crt'
    config.api_key = {"authorization": f"Bearer {token}"}
    with open('/tmp/ca.crt', 'w') as f:
        f.write(base64.b64decode(cluster['certificateAuthority']['data']).decode('utf-8'))
    return client.AppsV1Api(client.ApiClient(config))

def scale_deployment(nf, namespace, replicas):
    k8s = get_k8s_client()
    k8s.patch_namespaced_deployment_scale(name=nf, namespace=namespace, body={'spec': {'replicas': replicas}})
    return {'success': True, 'message': f'Scaled {nf} to {replicas}'}

def decimal_default(obj):
    if isinstance(obj, Decimal): return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError

def handle_heal_mode(event):
    headers = {'Content-Type':'application/json','Access-Control-Allow-Origin':'*'}
    method = event.get('httpMethod', 'GET')
    lam = boto3.client('lambda')
    fn_name = 'telco-buddy-agent-diagnose'
    if method == 'GET':
        cfg = lam.get_function_configuration(FunctionName=fn_name)
        mode = cfg.get('Environment', {}).get('Variables', {}).get('HEAL_MODE', 'APPROVAL_REQUIRED')
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'heal_mode': mode})}
    body = json.loads(event.get('body', '{}'))
    enabled = body.get('enabled', False)
    mode = 'AUTO' if enabled else 'APPROVAL_REQUIRED'
    cfg = lam.get_function_configuration(FunctionName=fn_name)
    env = cfg.get('Environment', {}).get('Variables', {})
    env['HEAL_MODE'] = mode
    lam.update_function_configuration(FunctionName=fn_name, Environment={'Variables': env})
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'heal_mode': mode, 'message': f'Heal mode set to {mode}'})}

def lambda_handler(event, context):
    headers = {'Content-Type':'application/json','Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'*','Access-Control-Allow-Methods':'*'}
    path = event.get('path', '')
    if 'heal-mode' in path:
        return handle_heal_mode(event)
    method = event.get('httpMethod', 'GET')
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': '{}'}
    if method == 'GET':
        r = approvals_table.scan(FilterExpression='#s = :p', ExpressionAttributeNames={'#s': 'status'}, ExpressionAttributeValues={':p': 'PENDING'})
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'approvals': r.get('Items', [])}, default=decimal_default)}
    elif method == 'POST':
        body = json.loads(event['body'])
        action = body.get('action', 'approve')
        now = datetime.utcnow().isoformat() + 'Z'
        if action == 'rollback':
            target = body.get('target', '')
            try:
                result = scale_deployment(target, 'open5gs', 0)
                return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': f'Rolled back {target}', 'result': result})}
            except Exception as e:
                return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}
        action_id = body.get('approval_id') or body.get('action_id')
        approval = approvals_table.get_item(Key={'approval_id': action_id}).get('Item')
        if not approval:
            return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Approval not found'})}
        if action == 'approve':
            approvals_table.update_item(Key={'approval_id': action_id},
                UpdateExpression='SET #s = :a, approved_at = :now',
                ExpressionAttributeNames={'#s': 'status'}, ExpressionAttributeValues={':a': 'APPROVED', ':now': now})
            try:
                result = scale_deployment(approval['target'], approval.get('namespace', 'open5gs'), 1)
            except Exception as e:
                result = {'success': False, 'error': str(e)}
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'Approved', 'healing_result': result}, default=decimal_default)}
        elif action == 'reject':
            approvals_table.update_item(Key={'approval_id': action_id},
                UpdateExpression='SET #s = :r, rejected_at = :now',
                ExpressionAttributeNames={'#s': 'status'}, ExpressionAttributeValues={':r': 'REJECTED', ':now': now})
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'Rejected'})}
    return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Invalid request'})}
