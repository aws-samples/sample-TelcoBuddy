import json, boto3, base64, os, urllib3, datetime as dt
from botocore.auth import SigV4QueryAuth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

REGION = os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
CLUSTER = os.environ.get('CLUSTER_NAME', 'telco-buddy-5g-cluster')
NAMESPACE = os.environ.get('NAMESPACE', 'open5gs')
K8S_ROLE_ARN = os.environ.get('K8S_ROLE_ARN', '')
_endpoint = None
_assumed = None

def _assume():
    global _assumed
    if _assumed: return _assumed
    if not K8S_ROLE_ARN: return None
    _assumed = boto3.client('sts').assume_role(RoleArn=K8S_ROLE_ARN, RoleSessionName='tools')['Credentials']
    return _assumed

def _token():
    a = _assume()
    creds = Credentials(a['AccessKeyId'], a['SecretAccessKey'], a['SessionToken']) if a else boto3.Session().get_credentials().get_frozen_credentials()
    req = AWSRequest(method='GET', url=f'https://sts.{REGION}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15', headers={'x-k8s-aws-id': CLUSTER})
    SigV4QueryAuth(creds, 'sts', REGION, expires=60).add_auth(req)
    return 'k8s-aws-v1.' + base64.urlsafe_b64encode(req.url.encode()).rstrip(b'=').decode()

def _k8s(method, path, body=None):
    global _endpoint
    if not _endpoint:
        a = _assume()
        kw = dict(region_name=REGION)
        if a: kw.update(aws_access_key_id=a['AccessKeyId'], aws_secret_access_key=a['SecretAccessKey'], aws_session_token=a['SessionToken'])
        _endpoint = boto3.client('eks', **kw).describe_cluster(name=CLUSTER)['cluster']['endpoint']
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    headers = {'Authorization': f'Bearer {_token()}'}
    if body: headers['Content-Type'] = 'application/strategic-merge-patch+json' if method == 'PATCH' else 'application/json'
    r = http.request(method, f'{_endpoint}{path}', headers=headers, body=body, timeout=15.0)
    return json.loads(r.data)

def lambda_handler(event, context):
    fn = event.get('function', '')
    params = {p['name']: p['value'] for p in event.get('parameters', [])}
    try:
        if fn == 'get_deployment_status':
            deps = _k8s('GET', f'/apis/apps/v1/namespaces/{NAMESPACE}/deployments')
            result = {d['metadata']['name']: {'desired': d['spec']['replicas'], 'available': d['status'].get('availableReplicas',0), 'ready': d['status'].get('readyReplicas',0)} for d in deps.get('items',[])}
        elif fn == 'get_pod_logs':
            nf = params.get('nf_name','')
            pods = _k8s('GET', f'/api/v1/namespaces/{NAMESPACE}/pods?labelSelector=app={nf}')
            items = pods.get('items',[])
            if not items: result = f"No pods for {nf}"
            else:
                pod = items[0]['metadata']['name']
                http = urllib3.PoolManager(cert_reqs='CERT_NONE')
                r = http.request('GET', f'{_endpoint}/api/v1/namespaces/{NAMESPACE}/pods/{pod}/log?tailLines=50', headers={'Authorization': f'Bearer {_token()}'}, timeout=15.0)
                result = r.data.decode()[:3000]
        elif fn == 'get_k8s_events':
            nf = params.get('nf_name','')
            evts = _k8s('GET', f'/api/v1/namespaces/{NAMESPACE}/events')
            result = [e['message'] for e in evts.get('items',[]) if nf in e.get('involvedObject',{}).get('name','')][-10:]
        elif fn == 'get_nf_dependencies':
            nf = params.get('nf_name','')
            svcs = {s['metadata']['name'] for s in _k8s('GET', f'/api/v1/namespaces/{NAMESPACE}/services').get('items',[])}
            cms = _k8s('GET', f'/api/v1/namespaces/{NAMESPACE}/configmaps')
            deps = set()
            for cm in cms.get('items',[]):
                if nf not in cm['metadata']['name']: continue
                raw = json.dumps(cm.get('data',{}))
                for s in svcs:
                    if s in raw and s != nf: deps.add(s)
            result = sorted(deps) if deps else ['No dependencies found']
        elif fn == 'scale_deployment':
            nf = params.get('nf_name','')
            replicas = int(params.get('replicas', 1))
            patch = json.dumps({"spec": {"replicas": replicas}}).encode()
            result = _k8s('PATCH', f'/apis/apps/v1/namespaces/{NAMESPACE}/deployments/{nf}/scale', patch)
        elif fn == 'restart_deployment':
            nf = params.get('nf_name','')
            patch = json.dumps({"spec":{"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt": dt.datetime.utcnow().isoformat()+"Z"}}}}}).encode()
            result = _k8s('PATCH', f'/apis/apps/v1/namespaces/{NAMESPACE}/deployments/{nf}', patch)
            result = {"status": "restarted", "deployment": nf}
        elif fn == 'scale_nodegroup':
            desired = int(params.get('desired_size', 2))
            eks = boto3.client('eks', region_name=REGION)
            ngs = eks.list_nodegroups(clusterName=CLUSTER)['nodegroups']
            if not ngs: result = {'error': 'No nodegroups found'}
            else:
                ng = ngs[0]
                eks.update_nodegroup_config(clusterName=CLUSTER, nodegroupName=ng,
                    scalingConfig={'minSize': max(1, desired), 'maxSize': max(2, desired), 'desiredSize': desired})
                result = {'status': 'scaling', 'nodegroup': ng, 'desired_size': desired}
        elif fn == 'get_nodegroup_status':
            eks = boto3.client('eks', region_name=REGION)
            ngs = eks.list_nodegroups(clusterName=CLUSTER)['nodegroups']
            result = {}
            for ng in ngs:
                info = eks.describe_nodegroup(clusterName=CLUSTER, nodegroupName=ng)['nodegroup']
                result[ng] = {'status': info['status'], 'desired': info['scalingConfig']['desiredSize'],
                    'min': info['scalingConfig']['minSize'], 'max': info['scalingConfig']['maxSize'],
                    'instance_type': info['instanceTypes'][0]}
        else:
            result = {'error': f'Unknown function: {fn}'}
    except Exception as e:
        result = {'error': str(e)}
    return {'response':{'actionGroup':event.get('actionGroup',''),'function':fn,'functionResponse':{'responseBody':{'TEXT':{'body':json.dumps(result,default=str)}}}}}
