import json, boto3, base64, time, os
from datetime import datetime
from kubernetes import client
from botocore.signers import RequestSigner

CORS_HEADERS = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST,OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type'}
AGENT_ID = os.environ.get('AGENT_ID', 'PLACEHOLDER')
AGENT_ALIAS_ID = os.environ.get('AGENT_ALIAS_ID', 'PLACEHOLDER')

# ── Fault Catalog ── aligned with 3GPP KB docs & deployed Open5GS 5G SA NFs ──
FAULT_CATALOG = {
    # ═══════════════════════════════════════════════════════════════════════════
    # INFRA — Pod crashes (scale_zero) for each deployed NF
    # ═══════════════════════════════════════════════════════════════════════════
    'INFRA-001': {'name': 'AMF Pod Crash',      'nf': 'amf',     'category': 'INFRA', 'severity': 'Critical', 'ref': 'TS 23.501', 'action': 'scale_zero'},
    'INFRA-002': {'name': 'SMF Pod Crash',      'nf': 'smf',     'category': 'INFRA', 'severity': 'Critical', 'ref': 'TS 23.502', 'action': 'scale_zero'},
    'INFRA-003': {'name': 'UPF Pod Crash',      'nf': 'upf',     'category': 'INFRA', 'severity': 'Critical', 'ref': 'TS 23.501', 'action': 'scale_zero'},
    'INFRA-004': {'name': 'NRF Pod Crash',      'nf': 'nrf',     'category': 'INFRA', 'severity': 'High',     'ref': 'TS 29.510', 'action': 'scale_zero'},
    'INFRA-005': {'name': 'UDR Pod Crash',      'nf': 'udr',     'category': 'INFRA', 'severity': 'High',     'ref': 'TS 29.504', 'action': 'scale_zero'},
    'INFRA-006': {'name': 'PCF Pod Crash',      'nf': 'pcf',     'category': 'INFRA', 'severity': 'High',     'ref': 'TS 29.507', 'action': 'scale_zero'},
    'INFRA-007': {'name': 'AUSF Pod Crash',     'nf': 'ausf',    'category': 'INFRA', 'severity': 'High',     'ref': 'TS 29.509', 'action': 'scale_zero'},
    'INFRA-008': {'name': 'UDM Pod Crash',      'nf': 'udm',     'category': 'INFRA', 'severity': 'High',     'ref': 'TS 29.503', 'action': 'scale_zero'},
    'INFRA-009': {'name': 'NSSF Pod Crash',     'nf': 'nssf',    'category': 'INFRA', 'severity': 'Medium',   'ref': 'TS 29.531', 'action': 'scale_zero'},
    'INFRA-010': {'name': 'SCP Pod Crash',      'nf': 'scp',     'category': 'INFRA', 'severity': 'High',     'ref': 'TS 29.500', 'action': 'scale_zero'},
    'INFRA-011': {'name': 'BSF Pod Crash',      'nf': 'bsf',     'category': 'INFRA', 'severity': 'Medium',   'ref': 'TS 29.521', 'action': 'scale_zero'},
    'INFRA-012': {'name': 'MongoDB Crash',      'nf': 'mongodb',  'category': 'INFRA', 'severity': 'Critical', 'ref': 'TS 23.501', 'action': 'scale_zero'},

    # ═══════════════════════════════════════════════════════════════════════════
    # PERF — Performance degradation / overload (log-only, no pod kill)
    # ═══════════════════════════════════════════════════════════════════════════
    # AMF performance (TS 38.413, TS 23.502, TS 28.552)
    'PERF-001': {'name': 'AMF NGAP Overload',                  'nf': 'amf',     'category': 'PERF', 'severity': 'Critical', 'ref': 'TS 38.413', 'action': 'log'},
    'PERF-002': {'name': 'AMF Registration Storm',             'nf': 'amf',     'category': 'PERF', 'severity': 'Critical', 'ref': 'TS 28.552', 'action': 'log'},
    'PERF-003': {'name': 'AMF Paging Congestion',              'nf': 'amf',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 23.502', 'action': 'log'},
    # SMF performance (TS 29.502, TS 29.244)
    'PERF-004': {'name': 'SMF Session Storm',                  'nf': 'smf',     'category': 'PERF', 'severity': 'Critical', 'ref': 'TS 29.502', 'action': 'log'},
    'PERF-005': {'name': 'N4 PFCP Timeout',                    'nf': 'smf',     'category': 'PERF', 'severity': 'Critical', 'ref': 'TS 29.244', 'action': 'log'},
    'PERF-006': {'name': 'SMF PDU Session Backlog',            'nf': 'smf',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 29.502', 'action': 'log'},
    # UPF performance (TS 29.281, TS 23.501)
    'PERF-007': {'name': 'GTP-U Packet Loss',                  'nf': 'upf',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 29.281', 'action': 'log'},
    'PERF-008': {'name': 'UPF N3 Throughput Degradation',      'nf': 'upf',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 29.281', 'action': 'log'},
    'PERF-009': {'name': 'UPF CPU Overload',                   'nf': 'upf',     'category': 'PERF', 'severity': 'Critical', 'ref': 'TS 23.501', 'action': 'log'},
    'PERF-010': {'name': 'UPF N6 Latency Spike',              'nf': 'upf',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 23.501', 'action': 'log'},
    # NRF performance (TS 29.510)
    'PERF-011': {'name': 'NRF Discovery Latency Spike',        'nf': 'nrf',     'category': 'PERF', 'severity': 'Medium',   'ref': 'TS 29.510', 'action': 'log'},
    'PERF-012': {'name': 'NRF Stale NF Profile Cache',         'nf': 'nrf',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 29.510', 'action': 'log'},
    # PCF performance (TS 29.507, TS 29.512)
    'PERF-013': {'name': 'PCF Policy Decision Latency',        'nf': 'pcf',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 29.512', 'action': 'log'},
    'PERF-014': {'name': 'PCF PCC Rule Overload',              'nf': 'pcf',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 29.507', 'action': 'log'},
    # UDR/UDM performance (TS 29.504, TS 29.503)
    'PERF-015': {'name': 'UDR Database Query Latency',         'nf': 'udr',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 29.504', 'action': 'log'},
    'PERF-016': {'name': 'UDM Subscription Data Overload',     'nf': 'udm',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 29.503', 'action': 'log'},
    # MongoDB performance
    'PERF-017': {'name': 'MongoDB Replication Lag',            'nf': 'mongodb',  'category': 'PERF', 'severity': 'High',     'ref': 'TS 23.501', 'action': 'log'},
    'PERF-018': {'name': 'MongoDB Connection Pool Exhaustion', 'nf': 'mongodb',  'category': 'PERF', 'severity': 'Critical', 'ref': 'TS 23.501', 'action': 'log'},
    # NSSF performance (TS 29.531)
    'PERF-019': {'name': 'NSSF Slice Selection Latency',       'nf': 'nssf',    'category': 'PERF', 'severity': 'Medium',   'ref': 'TS 29.531', 'action': 'log'},
    # SCP performance (TS 29.500)
    'PERF-020': {'name': 'SCP Proxy Overload',                 'nf': 'scp',     'category': 'PERF', 'severity': 'High',     'ref': 'TS 29.500', 'action': 'log'},
    # AUSF performance (TS 29.509)
    'PERF-021': {'name': 'AUSF Auth Vector Exhaustion',        'nf': 'ausf',    'category': 'PERF', 'severity': 'Critical', 'ref': 'TS 29.509', 'action': 'log'},

    # ═══════════════════════════════════════════════════════════════════════════
    # APP — Application / protocol-level faults (log-only)
    # ═══════════════════════════════════════════════════════════════════════════
    # NAS / Registration (TS 24.501)
    'APP-001': {'name': 'NAS Auth Failure Spike',              'nf': 'amf',     'category': 'APP', 'severity': 'Critical', 'ref': 'TS 24.501', 'action': 'log'},
    'APP-002': {'name': 'NAS Registration Reject Storm',       'nf': 'amf',     'category': 'APP', 'severity': 'Critical', 'ref': 'TS 24.501', 'action': 'log'},
    'APP-003': {'name': 'NAS Deregistration Flood',            'nf': 'amf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 24.501', 'action': 'log'},
    # PDU Session (TS 24.501, TS 29.502)
    'APP-004': {'name': 'PDU Session Reject Storm',            'nf': 'smf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 24.501', 'action': 'log'},
    'APP-005': {'name': 'PDU Session Modification Failure',    'nf': 'smf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 29.502', 'action': 'log'},
    # PFCP (TS 29.244)
    'APP-006': {'name': 'PFCP Association Lost',               'nf': 'smf',     'category': 'APP', 'severity': 'Critical', 'ref': 'TS 29.244', 'action': 'log'},
    'APP-007': {'name': 'PFCP Session Report Failure',         'nf': 'upf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 29.244', 'action': 'log'},
    # SBI / Service-Based Architecture (TS 29.500)
    'APP-008': {'name': 'SBI TLS Cert Expired',                'nf': 'nrf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 29.500', 'action': 'log'},
    'APP-009': {'name': 'OAuth2 Token Expiry Storm',           'nf': 'scp',     'category': 'APP', 'severity': 'High',     'ref': 'TS 29.500', 'action': 'log'},
    'APP-010': {'name': 'NF Service Deregistration',           'nf': 'nrf',     'category': 'APP', 'severity': 'Critical', 'ref': 'TS 29.510', 'action': 'log'},
    # Security (TS 33.501)
    'APP-011': {'name': '5G-AKA Authentication Failure',       'nf': 'ausf',    'category': 'APP', 'severity': 'Critical', 'ref': 'TS 33.501', 'action': 'log'},
    'APP-012': {'name': 'Security Context Mismatch',           'nf': 'amf',     'category': 'APP', 'severity': 'Critical', 'ref': 'TS 33.501', 'action': 'log'},
    # Mobility (TS 23.502, TS 38.423)
    'APP-013': {'name': 'Xn Handover Failure',                 'nf': 'amf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 38.423', 'action': 'log'},
    'APP-014': {'name': 'UE Context Release Storm',            'nf': 'amf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 23.502', 'action': 'log'},
    'APP-015': {'name': 'Idle-Connected Transition Failure',   'nf': 'amf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 23.502', 'action': 'log'},
    # Policy (TS 29.512, TS 29.514)
    'APP-016': {'name': 'PCC Rule Install Failure',            'nf': 'pcf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 29.512', 'action': 'log'},
    'APP-017': {'name': 'BSF Binding Discovery Failure',       'nf': 'bsf',     'category': 'APP', 'severity': 'Medium',   'ref': 'TS 29.521', 'action': 'log'},
    # Subscriber Data (TS 29.503, TS 29.504)
    'APP-018': {'name': 'UDM Auth Credential Corruption',      'nf': 'udm',     'category': 'APP', 'severity': 'Critical', 'ref': 'TS 29.503', 'action': 'log'},
    'APP-019': {'name': 'UDR Data Consistency Failure',        'nf': 'udr',     'category': 'APP', 'severity': 'High',     'ref': 'TS 29.504', 'action': 'log'},
    # Network Slicing (TS 29.531, TS 28.541)
    'APP-020': {'name': 'Slice Selection Failure',             'nf': 'nssf',    'category': 'APP', 'severity': 'High',     'ref': 'TS 29.531', 'action': 'log'},
    'APP-021': {'name': 'Slice SLA Violation',                 'nf': 'nssf',    'category': 'APP', 'severity': 'Critical', 'ref': 'TS 28.541', 'action': 'log'},
    # QoS (TS 23.501)
    'APP-022': {'name': 'QoS Flow Setup Failure',              'nf': 'smf',     'category': 'APP', 'severity': 'High',     'ref': 'TS 23.501', 'action': 'log'},
    'APP-023': {'name': 'GBR QoS Violation',                   'nf': 'upf',     'category': 'APP', 'severity': 'Critical', 'ref': 'TS 23.501', 'action': 'log'},
    # Event Exposure (TS 29.518, TS 29.522)
    'APP-024': {'name': 'AMF Event Subscription Overflow',     'nf': 'amf',     'category': 'APP', 'severity': 'Medium',   'ref': 'TS 29.518', 'action': 'log'},
    'APP-025': {'name': 'MongoDB Write Conflict',              'nf': 'mongodb', 'category': 'APP', 'severity': 'High',     'ref': 'TS 23.501', 'action': 'log'},
}

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
approvals_table = dynamodb.Table(os.environ.get('APPROVALS_TABLE', 'telco-buddy-approvals'))

CLUSTER_NAME = os.environ.get('CLUSTER_NAME', 'telco-buddy-5g-cluster')
K8S_ROLE_ARN = os.environ.get('K8S_ROLE_ARN', '')

def _get_assumed_credentials():
    if K8S_ROLE_ARN:
        sts = boto3.client('sts')
        creds = sts.assume_role(RoleArn=K8S_ROLE_ARN, RoleSessionName='chaos-engine')['Credentials']
        return boto3.Session(
            aws_access_key_id=creds['AccessKeyId'],
            aws_secret_access_key=creds['SecretAccessKey'],
            aws_session_token=creds['SessionToken'])
    return boto3.Session()

def get_eks_token(cluster_name=None):
    cluster_name = cluster_name or CLUSTER_NAME
    session = _get_assumed_credentials()
    sts = session.client('sts', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    signer = RequestSigner(sts.meta.service_model.service_id, os.environ.get('AWS_REGION', 'us-east-1'), 'sts', 'v4',
        sts._request_signer._credentials, sts.meta.events)
    params = {'method': 'GET', 'url': f'https://sts.{os.environ.get("AWS_REGION", "us-east-1")}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15',
        'body': {}, 'headers': {'x-k8s-aws-id': cluster_name}, 'context': {}}
    signed_url = signer.generate_presigned_url(params, region_name=os.environ.get('AWS_REGION', 'us-east-1'), expires_in=60, operation_name='')
    return 'k8s-aws-v1.' + base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8').rstrip('=')

def get_k8s_client():
    session = _get_assumed_credentials()
    eks = session.client('eks', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    cluster = eks.describe_cluster(name=CLUSTER_NAME)['cluster']
    config = client.Configuration()
    config.host = cluster['endpoint']
    config.verify_ssl = True
    config.ssl_ca_cert = '/tmp/ca.crt'
    config.api_key = {"authorization": f"Bearer {get_eks_token()}"}
    with open('/tmp/ca.crt', 'w') as f:
        f.write(base64.b64decode(cluster['certificateAuthority']['data']).decode('utf-8'))
    return client.AppsV1Api(client.ApiClient(config))

def invoke_bedrock_agent(fault_id, fault, nf_target, heal_allowed=True):
    try:
        bedrock = boto3.client('bedrock-agent-runtime')
        session_id = f"{fault_id}-{int(time.time())}"
        heal_instruction = (
            "Provide: 1) Root cause analysis 2) Impact on 5G services 3) Recommended healing action 4) Affected dependencies"
            if heal_allowed else
            "Provide: 1) Root cause analysis 2) Impact on 5G services 3) Recommended healing action (DO NOT execute it — approval is pending) 4) Affected dependencies\n"
            "IMPORTANT: Do NOT scale, restart, or modify any deployments. Only diagnose and recommend. The operator must approve before healing."
        )
        prompt = (f"Analyze this 5G network fault:\n"
                  f"Fault: {fault['name']} ({fault_id})\n"
                  f"Category: {fault['category']}\n"
                  f"Severity: {fault['severity']}\n"
                  f"Affected NF: {nf_target}\n"
                  f"3GPP Reference: {fault['ref']}\n\n"
                  f"{heal_instruction}")
        resp = bedrock.invoke_agent(agentId=AGENT_ID, agentAliasId=AGENT_ALIAS_ID, sessionId=session_id, inputText=prompt)
        diagnosis = ""
        for evt in resp.get('completion', []):
            if 'chunk' in evt and 'bytes' in evt['chunk']:
                diagnosis += evt['chunk']['bytes'].decode('utf-8')
        return diagnosis or "Agent returned empty response"
    except Exception as e:
        print(f"Bedrock error: {e}")
        return f"Agent diagnosis failed: {str(e)}"

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    # Async callback — diagnose then create approval record
    if event.get('_async_diagnose'):
        e = event
        try:
            diag = invoke_bedrock_agent(e['fault_id'], e['fault'], e['target'], heal_allowed=e.get('heal_allowed', True))
        except Exception as ex:
            diag = f'Diagnosis failed: {str(ex)[:200]}'
        approvals_table.put_item(Item={
            'approval_id': e['approval_id'], 'target': e['target'],
            'status': e['status'], 'action_type': e['action_type'],
            'fault_id': e['fault_id'], 'category': e['category'],
            'description': e['description'], 'diagnosis': diag,
            'namespace': e['namespace'],
            'created_at': e['created_at'],
            'ttl': int(time.time()) + 2592000
        })
        return

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    body = json.loads(event['body']) if isinstance(event.get('body'), str) else event
    action = body.get('action', 'inject')

    if action == 'catalog':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps(FAULT_CATALOG)}

    if action == 'rollback_all':
        try:
            k8s = get_k8s_client()
            restored = []
            for dep in k8s.list_namespaced_deployment('open5gs').items:
                if dep.spec.replicas == 0:
                    k8s.patch_namespaced_deployment_scale(name=dep.metadata.name, namespace='open5gs', body={'spec': {'replicas': 1}})
                    restored.append(dep.metadata.name)
            return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': json.dumps({'status': 'rolled_back', 'restored': restored})}
        except Exception as e:
            return {'statusCode': 500, 'headers': CORS_HEADERS, 'body': json.dumps({'error': str(e)})}

    fault_id = body.get('fault_id')
    if fault_id not in FAULT_CATALOG:
        return {'statusCode': 400, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Invalid fault_id'})}

    fault = FAULT_CATALOG[fault_id]
    heal_mode = body.get('heal_mode', 'AUTONOMOUS')
    namespace = body.get('namespace', 'open5gs')
    deployment_name = None

    if fault['action'] == 'scale_zero':
        try:
            k8s = get_k8s_client()
            for dep in k8s.list_namespaced_deployment(namespace).items:
                if fault['nf'].lower() in dep.metadata.name.lower():
                    deployment_name = dep.metadata.name
                    break
            if not deployment_name:
                return {'statusCode': 404, 'headers': CORS_HEADERS, 'body': json.dumps({'error': f"No deployment for {fault['nf']}"})}
            k8s.patch_namespaced_deployment_scale(name=deployment_name, namespace=namespace, body={'spec': {'replicas': 0}})
        except Exception as e:
            return {'statusCode': 500, 'headers': CORS_HEADERS, 'body': json.dumps({'error': str(e)})}
    else:
        deployment_name = fault['nf']

    action_id = f"{fault['category']}-{fault_id.split('-')[1]}-agent-{str(int(time.time()))[-8:]}"

    # Store heal_mode for agent-diagnose to pick up via env
    os.environ['HEAL_MODE'] = heal_mode

    # Chaos engine only crashes the pod. 
    # Prometheus detects (~10s) → AlertManager fires webhook → agent-diagnose handles diagnosis + approval
    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({
            'status': 'pending_approval' if heal_mode == 'APPROVAL_REQUIRED' else 'injected',
            'fault_id': fault_id, 'deployment': deployment_name or fault['nf'],
            'action_id': action_id, 'diagnosis_logged': True, 'namespace': namespace
        })
    }
