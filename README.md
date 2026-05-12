# Telco Buddy — Autonomous 5G Network Operations Agent

Telco Buddy is an AI-powered autonomous operations agent for 5G/4G core networks on AWS. It detects network function faults via Prometheus, diagnoses root cause using an Amazon Bedrock Agent grounded in 3GPP specs, and remediates with operator approval via EKS. Includes a 34-scenario chaos lab and an operator dashboard.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Amazon EKS (5G core cluster)                               │
│  ├── open5gs: AMF, SMF, UPF, NRF, UDM, UDR, AUSF, PCF,      │
│  │            NSSF, BSF, SCP, MongoDB, WebUI                │
│  ├── Monitoring: Prometheus + AlertManager                  │
│  └── PrometheusRules (6 alert rules)                        │
│         │                                                   │
│         ▼ AlertManager webhook                              │
│  Amazon API Gateway → Lambda (agent-diagnose)               │
│         │                                                   │
│         ▼                                                   │
│  Amazon Bedrock Agent (Claude Sonnet)                       │
│  ├── Knowledge Base (3GPP specs on Amazon OpenSearch)       │
│  └── 5 Investigation tools (agent-tools Lambda, in VPC)     │
│         │                                                   │
│         ▼                                                   │
│  Amazon DynamoDB (issues + approvals)                       │
│         │                                                   │
│         ▼                                                   │
│  Operator Dashboard (Amazon CloudFront + S3)                │
│         │                                                   │
│         ▼                                                   │
│  Approval → kubectl heal (via agent-tools Lambda)           │
└─────────────────────────────────────────────────────────────┘
```

## What's in this repository

| Component | Location |
|---|---|
| CDK stacks (10) | `stacks/` |
| Lambda source code | `lambda-src/` |
| Kubernetes manifests for 5G NFs | `k8s-manifests/` |
| Operator dashboard | `ui/` |
| Knowledge base stubs | `kb-docs/` |
| App entry point | `app.py` |
| Configuration | `config.py`, `cdk.json` |

## Prerequisites

- AWS account with Amazon Bedrock enabled (Claude Sonnet access)
- AWS CDK v2 (`npm install -g aws-cdk`)
- Python 3.12+
- `kubectl` (for post-deploy verification)

## Deploy

```bash
# 1. Clone and install
git clone https://github.com/aws-samples/sample-TelcoBuddy.git
cd sample-TelcoBuddy
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Fetch kubectl for Lambda layer (see lambda-src/kubectl-layer/README.md)
cd lambda-src/kubectl-layer && mkdir -p python
curl -L https://dl.k8s.io/release/v1.31.0/bin/linux/amd64/kubectl -o python/kubectl
chmod +x python/kubectl
cd ../..

# 3. Configure cdk.json (account, region — default us-east-1)

# 4. Bootstrap and deploy
cdk bootstrap
cdk deploy --all
```

## Components deployed

10 CDK stacks:

| Stack | Purpose |
|---|---|
| `telco-buddy-v2-network` | VPC, subnets, NAT gateway |
| `telco-buddy-v2-eks` | EKS cluster, nodegroup, k8s-admin role |
| `telco-buddy-v2-open5gs` | 5G NF Kubernetes manifests |
| `telco-buddy-v2-monitoring` | Prometheus + AlertManager |
| `telco-buddy-v2-storage` | DynamoDB tables (issues, approvals) |
| `telco-buddy-v2-ai-engine` | Bedrock Agent, Knowledge Base, diagnose Lambda |
| `telco-buddy-v2-investigation` | Agent tools Lambda with VPC access |
| `telco-buddy-v2-chaos-lab` | Chaos engine Lambda |
| `telco-buddy-v2-api` | API Gateway + AlertManager webhook |
| `telco-buddy-v2-ui` | S3 + CloudFront operator dashboard |

## Chaos scenarios (34 total)

- **14 Infrastructure** (pod crash on each 5G NF)
- **10 Performance** (NGAP overload, session storms, throughput degradation)
- **10 Application** (NAS auth failure, PDU session failure, PFCP issues, etc.)

All 3GPP-compliant with proper spec references (TS 23.501, 29.510, 38.413, etc.).

## Security

- See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
- Uses IAM roles only; no hardcoded secrets.
- API Gateway uses public endpoints for demo mode. For production, add Cognito/IAM auth.

## Cost

- EKS (2× m5.xlarge): ~$0.38/hr (~$9/day)
- Lambda + Bedrock + CloudWatch: minimal (pay per use)
- **Total: ~$10/day when running**

Scale EKS nodegroup to 0 when not in use to save cost.

## License

MIT-0. See [LICENSE](LICENSE).
