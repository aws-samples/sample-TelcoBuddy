"""Patches AlertManager secret with the actual API Gateway webhook URL."""
import json, boto3, base64, os, urllib3
from botocore.session import get_session
from botocore.auth import SigV4QueryAuth
from botocore.awsrequest import AWSRequest

def get_eks_token(cluster_name, region):
    creds = get_session().get_credentials().get_frozen_credentials()
    req = AWSRequest(method='GET',
        url=f'https://sts.{region}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15',
        headers={'x-k8s-aws-id': cluster_name})
    SigV4QueryAuth(creds, 'sts', region, expires=60).add_auth(req)
    return 'k8s-aws-v1.' + base64.urlsafe_b64encode(req.url.encode()).rstrip(b'=').decode()

def handler(event, context):
    if event.get('RequestType') == 'Delete':
        send_response(event, 'SUCCESS')
        return
    props = event['ResourceProperties']
    cluster_name = props['ClusterName']
    webhook_url = props['WebhookUrl']
    prefix = props['Prefix']
    region = os.environ.get('AWS_REGION')
    role_arn = props.get('K8sRoleArn')

    # Assume K8s admin role if provided
    if role_arn:
        sts = boto3.client('sts')
        creds = sts.assume_role(RoleArn=role_arn, RoleSessionName='patch-am')['Credentials']
        os.environ['AWS_ACCESS_KEY_ID'] = creds['AccessKeyId']
        os.environ['AWS_SECRET_ACCESS_KEY'] = creds['SecretAccessKey']
        os.environ['AWS_SESSION_TOKEN'] = creds['SessionToken']

    endpoint = boto3.client('eks', region_name=region).describe_cluster(
        name=cluster_name)['cluster']['endpoint']
    token = get_eks_token(cluster_name, region)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')

    am_config = json.dumps({
        "route": {"receiver": prefix,
                  "routes": [{"match": {"team": prefix}, "receiver": prefix,
                              "group_wait": "10s", "repeat_interval": "30s"}]},
        "receivers": [{"name": prefix,
                       "webhook_configs": [{"url": webhook_url, "send_resolved": True}]}]
    })

    secret = {"apiVersion": "v1", "kind": "Secret", "metadata": {
        "name": "alertmanager-prometheus-kube-prometheus-alertmanager",
        "namespace": "monitoring"},
        "stringData": {"alertmanager.yaml": am_config}}

    # Try patch first, create if not found
    for method in ['PATCH', 'POST']:
        url = f"{endpoint}/api/v1/namespaces/monitoring/secrets"
        if method == 'PATCH':
            url += "/alertmanager-prometheus-kube-prometheus-alertmanager"
            ct = 'application/strategic-merge-patch+json'
        else:
            ct = 'application/json'
        r = http.request(method, url, body=json.dumps(secret).encode(),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': ct})
        if r.status in (200, 201):
            send_response(event, 'SUCCESS')
            return
    send_response(event, 'FAILED', f'K8s API returned {r.status}: {r.data.decode()[:200]}')

def send_response(event, status, reason=''):
    import urllib.request
    body = json.dumps({'Status': status, 'Reason': reason or 'OK',
        'PhysicalResourceId': 'alertmanager-webhook-patch',
        'StackId': event['StackId'], 'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId']})
    urllib.request.urlopen(urllib.request.Request(
        event['ResponseURL'], data=body.encode(), method='PUT',
        headers={'Content-Type': ''}))
