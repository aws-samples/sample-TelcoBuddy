import json, boto3, os
from datetime import datetime, timedelta
from botocore.config import Config
from boto3.dynamodb.conditions import Attr

bedrock = boto3.client('bedrock-agent-runtime', config=Config(read_timeout=240, connect_timeout=10))
dynamodb = boto3.resource('dynamodb')
issues_table = dynamodb.Table(os.environ.get('ISSUES_TABLE', 'telco-buddy-issues'))
approvals_table = dynamodb.Table(os.environ.get('APPROVALS_TABLE', 'telco-buddy-approvals'))

AGENT_ID = os.environ.get('AGENT_ID', 'L5V4LTAKBD')
AGENT_ALIAS_ID = os.environ.get('AGENT_ALIAS_ID', 'VCY3ACKG4C')

VALID_NFS = {'amf', 'smf', 'upf', 'nrf', 'ausf', 'udm', 'udr', 'pcf', 'nssf', 'scp', 'bsf', 'mongodb', 'webui'}

# 3GPP TS 23.501 dependency graph — upstream NF failures suppress downstream alerts
NF_DEPENDENCIES = {
    'amf':  [],                          # AMF is root — no upstream
    'smf':  ['amf', 'nrf'],              # SMF depends on AMF for N11, NRF for discovery
    'upf':  ['smf'],                     # UPF depends on SMF for N4/PFCP
    'ausf': ['nrf'],                     # AUSF depends on NRF
    'udm':  ['nrf', 'udr'],             # UDM depends on NRF + UDR for data
    'udr':  ['mongodb'],                 # UDR depends on MongoDB
    'pcf':  ['nrf', 'udr'],             # PCF depends on NRF + UDR for policy data
    'nssf': ['nrf'],                     # NSSF depends on NRF
    'scp':  [],                          # SCP is infrastructure — no upstream
    'bsf':  ['nrf'],                     # BSF depends on NRF
    'nrf':  [],                          # NRF is root — no upstream
    'mongodb': [],                       # MongoDB is root — no upstream
    'webui': ['mongodb'],                # WebUI depends on MongoDB
}

DEDUP_WINDOW_MINUTES = 15
CORRELATION_WINDOW_SECONDS = 60


def _has_recent_issue(nf, alert_name):
    """Dedup: skip if same NF+alert has open issue within window."""
    cutoff = (datetime.utcnow() - timedelta(minutes=DEDUP_WINDOW_MINUTES)).isoformat() + 'Z'
    try:
        resp = issues_table.scan(
            FilterExpression=Attr('nf').eq(nf) & Attr('fault_id').eq(alert_name)
                & Attr('status').is_in(['PENDING_APPROVAL', 'PENDING', 'OPEN', 'APPROVED'])
                & Attr('timestamp').gte(cutoff),
            Limit=1, ProjectionExpression='issue_id'
        )
        return len(resp.get('Items', [])) > 0
    except Exception:
        return False


def _is_downstream_of_active_incident(nf):
    """Correlation: suppress if an upstream NF already has an active incident."""
    upstream_nfs = NF_DEPENDENCIES.get(nf, [])
    if not upstream_nfs:
        return False, None
    cutoff = (datetime.utcnow() - timedelta(seconds=CORRELATION_WINDOW_SECONDS)).isoformat() + 'Z'
    try:
        resp = issues_table.scan(
            FilterExpression=Attr('nf').is_in(upstream_nfs)
                & Attr('status').is_in(['PENDING_APPROVAL', 'PENDING', 'OPEN'])
                & Attr('timestamp').gte(cutoff),
            Limit=1, ProjectionExpression='issue_id,nf'
        )
        items = resp.get('Items', [])
        if items:
            return True, items[0].get('nf', '?')
    except Exception:
        pass
    return False, None


def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))

    # Direct chat/diagnose calls
    if 'prompt' in body or 'message' in body:
        prompt = body.get('prompt', body.get('message', ''))
        session_id = f"chat-{int(datetime.utcnow().timestamp())}"
        try:
            resp = bedrock.invoke_agent(agentId=AGENT_ID, agentAliasId=AGENT_ALIAS_ID,
                                        sessionId=session_id, inputText=prompt)
            diagnosis = ""
            for evt in resp.get('completion', []):
                if 'chunk' in evt:
                    diagnosis += evt['chunk'].get('bytes', b'').decode('utf-8')
            return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'diagnosis': diagnosis})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}

    # AlertManager webhook
    alerts = body.get('alerts', [])
    heal_mode = os.environ.get('HEAL_MODE', 'APPROVAL_REQUIRED')
    processed = 0
    skipped_dedup = 0
    skipped_correlated = 0

    for alert in alerts:
        if alert.get('status') == 'resolved':
            continue

        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        nf = labels.get('deployment', labels.get('pod', '')).lower().split('-')[0]
        namespace = labels.get('namespace', '')

        if nf not in VALID_NFS or namespace != 'open5gs':
            print(f"Skipping non-NF alert: {labels.get('alertname')} nf={nf} ns={namespace}")
            continue

        alert_name = labels.get('alertname', 'Unknown')
        severity = labels.get('severity', 'warning')
        category = labels.get('category', 'INFRA')

        # Phase 2a: Dedup — skip if same NF+alert already has open issue
        if _has_recent_issue(nf, alert_name):
            print(f"DEDUP: Skipping {alert_name} for {nf} — open issue exists within {DEDUP_WINDOW_MINUTES}min")
            skipped_dedup += 1
            continue

        # Phase 2b: Correlation — suppress downstream alerts if upstream NF is already down
        is_downstream, upstream_nf = _is_downstream_of_active_incident(nf)
        if is_downstream:
            print(f"CORRELATED: {nf} {alert_name} suppressed — upstream {upstream_nf} already has active incident")
            # Still log it as a correlated issue but don't invoke Bedrock
            issues_table.put_item(Item={
                'issue_id': f"corr-{alert_name}-{datetime.utcnow().strftime('%s')[-6:]}",
                'timestamp': datetime.utcnow().isoformat() + 'Z', 'nf': nf,
                'description': annotations.get('summary', f'{alert_name} on {nf}'),
                'jitu_diagnosis': f'Correlated with upstream {upstream_nf} failure. This is likely a cascading effect, not an independent fault. Will auto-resolve when {upstream_nf} is healed.',
                'status': 'CORRELATED', 'confidence': '85', 'source': 'correlation-engine',
                'metric': alert_name, 'fault_id': alert_name, 'event_type': 'correlated',
                'value': '1', 'upstream_nf': upstream_nf,
                'ttl': int(datetime.utcnow().timestamp()) + 2592000
            })
            skipped_correlated += 1
            continue

        # Build context-rich prompt with alert metadata
        impact = annotations.get('impact', '')
        issue_id = f"agent-{alert_name}-{datetime.utcnow().strftime('%s')[-6:]}"
        timestamp = datetime.utcnow().isoformat() + 'Z'

        prompt = (
            f"Diagnose this 5G network alert:\n"
            f"Alert: {alert_name}\n"
            f"Severity: {severity} | Category: {category}\n"
            f"NF: {nf} (namespace: {namespace})\n"
            f"Description: {annotations.get('summary', 'NF issue detected')}\n"
            f"Impact: {impact}\n"
            f"Known dependencies (3GPP TS 23.501): {nf} depends on {NF_DEPENDENCIES.get(nf, [])}\n\n"
            f"Provide: 1) Root cause analysis 2) Impact on 5G services per 3GPP specs "
            f"3) Recommended healing action 4) Affected dependencies\n"
            f"{'IMPORTANT: Do NOT execute any healing actions. Only diagnose and recommend. Approval is pending.' if heal_mode == 'APPROVAL_REQUIRED' else ''}"
        )

        try:
            response = bedrock.invoke_agent(agentId=AGENT_ID, agentAliasId=AGENT_ALIAS_ID,
                                            sessionId=issue_id, inputText=prompt)
            diagnosis = ""
            for evt in response.get('completion', []):
                if 'chunk' in evt:
                    diagnosis += evt['chunk'].get('bytes', b'').decode('utf-8')

            # Write approval with diagnosis FIRST
            if heal_mode == 'APPROVAL_REQUIRED':
                approvals_table.put_item(Item={
                    'approval_id': f"approval-{issue_id}", 'issue_id': issue_id,
                    'nf': nf, 'target': nf, 'namespace': namespace, 'fault_id': alert_name,
                    'action': f'Scale {nf} to 1 replica', 'status': 'PENDING',
                    'diagnosis': diagnosis,
                    'description': annotations.get('summary', f'{alert_name} on {nf}'),
                    'category': category, 'severity': severity,
                    'created_at': timestamp
                })

            # Then write issue
            issues_table.put_item(Item={
                'issue_id': issue_id, 'timestamp': timestamp, 'nf': nf,
                'description': annotations.get('summary', f'{alert_name} on {nf}'),
                'jitu_diagnosis': diagnosis,
                'status': 'PENDING_APPROVAL' if heal_mode == 'APPROVAL_REQUIRED' else 'OPEN',
                'confidence': '95', 'source': 'bedrock-agent', 'metric': alert_name,
                'fault_id': alert_name, 'event_type': 'agent_diagnosis', 'value': '1',
                'category': category, 'severity': severity,
                'ttl': int(datetime.utcnow().timestamp()) + 2592000
            })
            print(f"Created: {issue_id} ({alert_name} on {nf})")
            processed += 1

        except Exception as e:
            print(f"Error processing {alert_name} on {nf}: {e}")

    result = f"Processed {processed}, dedup={skipped_dedup}, correlated={skipped_correlated}, total={len(alerts)}"
    print(result)
    return {'statusCode': 200, 'body': json.dumps({'message': result})}
