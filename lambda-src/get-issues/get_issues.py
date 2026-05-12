import json, boto3, os, base64, urllib3
from botocore.session import get_session
from botocore.auth import SigV4QueryAuth
from botocore.awsrequest import AWSRequest

REGION = os.environ['AWS_REGION']
CLUSTER = os.environ.get('CLUSTER_NAME', '')
K8S_ROLE = os.environ.get('K8S_ROLE_ARN', '')

dynamodb = boto3.resource('dynamodb', region_name=REGION)
approvals_table = dynamodb.Table(os.environ.get('APPROVALS_TABLE', 'telco-buddy-approvals'))
issues_table = dynamodb.Table(os.environ.get('ISSUES_TABLE', 'telco-buddy-issues'))

NF_5G = ['nrf','scp','ausf','udm','udr','pcf','nssf','bsf','amf','smf','upf']

def get_eks_token(cluster):
    from botocore.credentials import Credentials
    if K8S_ROLE:
        c = boto3.client('sts').assume_role(RoleArn=K8S_ROLE, RoleSessionName='nf-status')['Credentials']
        creds = Credentials(c['AccessKeyId'], c['SecretAccessKey'], c['SessionToken'])
    else:
        creds = get_session().get_credentials().get_frozen_credentials()
    req = AWSRequest(method='GET',
        url=f'https://sts.{REGION}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15',
        headers={'x-k8s-aws-id': cluster})
    SigV4QueryAuth(creds, 'sts', REGION, expires=60).add_auth(req)
    return 'k8s-aws-v1.' + base64.urlsafe_b64encode(req.url.encode()).rstrip(b'=').decode()

def get_pod_status():
    if not CLUSTER: return {n: {'running': 1, 'desired': 1, 'restarts': 0} for n in NF_5G}
    try:
        endpoint = boto3.client('eks', region_name=REGION).describe_cluster(name=CLUSTER)['cluster']['endpoint']
        token = get_eks_token(CLUSTER)
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        r = http.request('GET', f'{endpoint}/api/v1/namespaces/open5gs/pods', headers={'Authorization': f'Bearer {token}'})
        if r.status != 200:
            print(f"EKS API returned {r.status}: {r.data[:200]}")
            return {}
        pods = json.loads(r.data)
        status = {}
        for pod in pods.get('items', []):
            name = pod['metadata'].get('labels', {}).get('app', pod['metadata']['name'].rsplit('-', 1)[0])
            cs = pod.get('status', {}).get('containerStatuses', [{}])[0]
            status[name] = {'running': 1 if cs.get('ready') else 0, 'desired': 1, 'restarts': cs.get('restartCount', 0)}
        return status
    except Exception as e:
        print(f"EKS query failed: {e}")
        return {}

def lambda_handler(event, context):
    path = event.get('path', '') or event.get('resource', '')

    if 'nf-status' in path:
        pod_status = get_pod_status()
        def build_nf(name):
            s = pod_status.get(name, {'running': 0, 'desired': 1, 'restarts': 0})
            return {'name': name.upper(), 'running': s['running'], 'desired': s['desired'],
                    'health': 100 if s['running'] >= s['desired'] else 0, 'restarts': s['restarts']}
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'5g': [build_nf(n) for n in NF_5G], 'epc': []})}

    # /issues — merge approvals + issues tables
    diag_map = {}
    try:
        for item in issues_table.scan()['Items']:
            iid = str(item.get('issue_id', ''))
            if iid: diag_map[iid] = str(item.get('jitu_diagnosis', ''))
    except Exception: pass

    results = []
    seen_nf = set()
    try:
        items = sorted(approvals_table.scan()['Items'], key=lambda x: str(x.get('created_at','')), reverse=True)
        for item in items:
            nf = str(item.get('nf', item.get('target', '')))
            if nf in seen_nf: continue
            seen_nf.add(nf)
            aid = str(item.get('approval_id', item.get('action_id','')))
            # Use 'diagnosis' from approvals table directly, fall back to issues table
            diagnosis = str(item.get('diagnosis', '')) or diag_map.get(aid, '')
            results.append({
                'issueId': aid,
                'timestamp': str(item.get('created_at','')),
                'nf': nf, 'description': str(item.get('action', item.get('description',''))),
                'status': str(item.get('status','PENDING')),
                'jitu_diagnosis': diagnosis,
                'confidence': '95', 'fault_id': str(item.get('fault_id','')),
                'metric': str(item.get('fault_id','')),
                'event_type': 'agent_diagnosis', 'source': 'bedrock-agent', 'value': '1'})
    except Exception as e:
        print(f"Approvals scan error: {e}")

    try:
        for item in issues_table.scan()['Items']:
            nf = str(item.get('nf',''))
            if nf in seen_nf: continue
            seen_nf.add(nf)
            results.append({
                'issueId': str(item.get('issue_id','')),
                'timestamp': str(item.get('timestamp', item.get('created_at',''))),
                'nf': nf, 'description': str(item.get('description','')),
                'status': str(item.get('status','')),
                'jitu_diagnosis': str(item.get('jitu_diagnosis','')),
                'confidence': str(item.get('confidence','90')),
                'fault_id': str(item.get('fault_id','')), 'metric': str(item.get('metric','')),
                'event_type': str(item.get('event_type','')), 'source': str(item.get('source','')), 'value': '1'})
    except Exception: pass

    results.sort(key=lambda x: x.get('timestamp',''), reverse=True)
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'issues': results})}
