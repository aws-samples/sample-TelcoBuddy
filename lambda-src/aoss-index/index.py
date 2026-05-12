"""Create AOSS vector index for Bedrock KB — waits for collection ACTIVE + policy propagation."""
import json, boto3, os, time, hashlib, urllib.request

def handler(event, context):
    try:
        if event.get('RequestType') == 'Delete':
            send_cfn(event, context, 'SUCCESS')
            return

        props = event.get('ResourceProperties', {})
        endpoint = props.get('Endpoint', '')
        index_name = props.get('IndexName', '')
        coll_name = props.get('CollectionName', '')
        region = os.environ['AWS_REGION']

        aoss_client = boto3.client('opensearchserverless', region_name=region)

        # Step 1: Wait for collection to be ACTIVE (up to 3 min)
        print(f"Waiting for collection {coll_name} to be ACTIVE...")
        for attempt in range(18):
            try:
                resp = aoss_client.batch_get_collection(names=[coll_name])
                details = resp.get('collectionDetails', [])
                if details and details[0].get('status') == 'ACTIVE':
                    print(f"Collection ACTIVE after {attempt * 10}s")
                    break
                status = details[0].get('status', 'UNKNOWN') if details else 'NOT_FOUND'
                print(f"Collection status: {status}, waiting 10s... ({attempt+1}/18)")
            except Exception as e:
                print(f"BatchGetCollection error: {e}, waiting 10s...")
            time.sleep(10)
        else:
            send_cfn(event, context, 'FAILED', f'Collection {coll_name} not ACTIVE after 3min')
            return

        # Step 2: Create index with retry for access policy propagation
        # CRITICAL: AOSS requires x-amz-content-sha256 header for write operations (PUT/POST).
        # Without it, AOSS returns 403 Forbidden even with correct data access policies.
        from botocore.auth import SigV4Auth
        from botocore.awsrequest import AWSRequest
        from botocore.httpsession import URLLib3Session

        session = boto3.Session()
        http = URLLib3Session()

        def make_request(method, url, body=None):
            creds = session.get_credentials().get_frozen_credentials()
            content_hash = hashlib.sha256(body or b'').hexdigest()
            headers = {
                "Content-Type": "application/json",
                "x-amz-content-sha256": content_hash,
            }
            req = AWSRequest(method=method, url=url, data=body, headers=headers)
            SigV4Auth(creds, "aoss", region).add_auth(req)
            resp = http.send(req.prepare())
            if resp.status_code >= 400:
                raise Exception(f"{resp.status_code} {resp.text[:200]}")
            return resp

        url = f"{endpoint}/{index_name}"

        # Check if index already exists
        try:
            make_request("GET", f"{endpoint}/_cat/indices/{index_name}")
            print(f"Index {index_name} already exists")
            send_cfn(event, context, 'SUCCESS')
            return
        except:
            pass

        body = json.dumps({
            "settings": {"index": {"knn": True}},
            "mappings": {"properties": {
                "bedrock-knowledge-base-default-vector": {
                    "type": "knn_vector", "dimension": 1024,
                    "method": {"engine": "faiss", "name": "hnsw", "space_type": "l2"}},
                "AMAZON_BEDROCK_TEXT_CHUNK": {"type": "text"},
                "AMAZON_BEDROCK_METADATA": {"type": "text"},
            }}
        }).encode()

        for attempt in range(40):
            try:
                resp = make_request("PUT", url, body)
                print(f"Created index: {resp.text[:200]}")
                send_cfn(event, context, 'SUCCESS')
                return
            except Exception as e:
                print(f"PUT attempt {attempt+1}/40: {e} — waiting 15s...")
                time.sleep(15)

        send_cfn(event, context, 'FAILED', 'Index creation failed after retries')
    except Exception as e:
        print(f"Error: {e}")
        send_cfn(event, context, 'FAILED', str(e)[:200])


def send_cfn(event, context, status, reason=''):
    body = json.dumps({
        'Status': status,
        'Reason': reason or f'See CloudWatch Log Stream: {context.log_stream_name}',
        'PhysicalResourceId': 'aoss-index',
        'StackId': event.get('StackId', ''),
        'RequestId': event.get('RequestId', ''),
        'LogicalResourceId': event.get('LogicalResourceId', ''),
    }).encode()
    req = urllib.request.Request(event['ResponseURL'], data=body, method='PUT',
        headers={'Content-Type': '', 'Content-Length': str(len(body))})
    urllib.request.urlopen(req)
