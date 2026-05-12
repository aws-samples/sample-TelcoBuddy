#!/bin/bash
# Telco Buddy — Post-Deploy Validation
# Usage: ./validate.sh <project-name> <region>
set -e

PN=${1:-telco-buddy-v2}
REGION=${2:-us-east-1}
PASS=0; FAIL=0

check() {
  if eval "$2" >/dev/null 2>&1; then
    echo "  ✅ $1"
    ((PASS++))
  else
    echo "  ❌ $1"
    ((FAIL++))
  fi
}

echo "═══════════════════════════════════════════════════"
echo "Validating: $PN in $REGION"
echo "═══════════════════════════════════════════════════"

# ── STEP 1: FOUNDATION ──
echo ""
echo "▶ STEP 1: FOUNDATION"
aws eks update-kubeconfig --name ${PN}-5g-cluster --region $REGION --quiet 2>/dev/null

check "EKS cluster reachable" "kubectl get nodes --no-headers 2>/dev/null | grep -q Ready"
check "Nodes ready (2)" "[ $(kubectl get nodes --no-headers 2>/dev/null | grep -c Ready) -ge 2 ]"
check "Namespace: open5gs" "kubectl get ns open5gs --no-headers 2>/dev/null"
check "Namespace: monitoring" "kubectl get ns monitoring --no-headers 2>/dev/null"
check "Prometheus running" "kubectl get pod -n monitoring -l app.kubernetes.io/name=prometheus --no-headers 2>/dev/null | grep -q Running"
check "AlertManager running" "kubectl get pod -n monitoring -l app.kubernetes.io/name=alertmanager --no-headers 2>/dev/null | grep -q Running"
check "Grafana running" "kubectl get pod -n monitoring -l app.kubernetes.io/name=grafana --no-headers 2>/dev/null | grep -q Running"
check "kube-state-metrics running" "kubectl get pod -n monitoring -l app.kubernetes.io/name=kube-state-metrics --no-headers 2>/dev/null | grep -q Running"
check "PrometheusRule exists" "kubectl get prometheusrule ${PN}-nf-alerts -n monitoring --no-headers 2>/dev/null"
check "kube-state-metrics scraping" "kubectl exec prometheus-prometheus-kube-prometheus-prometheus-0 -n monitoring -c prometheus -- sh -c 'wget -qO- http://localhost:9090/api/v1/query?query=up{job=\"kube-state-metrics\"}' 2>/dev/null | grep -q '\"value\"'"

# ── STEP 2: 5G CORE ──
echo ""
echo "▶ STEP 2: 5G CORE"
for nf in amf ausf bsf mongodb nrf nssf pcf scp smf udm udr upf webui; do
  check "NF $nf running" "kubectl get deploy $nf -n open5gs --no-headers 2>/dev/null | grep -q '1/1'"
done
check "Prometheus sees NFs" "kubectl exec prometheus-prometheus-kube-prometheus-prometheus-0 -n monitoring -c prometheus -- sh -c 'wget -qO- \"http://localhost:9090/api/v1/query?query=kube_deployment_spec_replicas{namespace=\\\"open5gs\\\"}\"' 2>/dev/null | grep -q deployment"

# ── STEP 3: AI BRAIN ──
echo ""
echo "▶ STEP 3: AI BRAIN"
check "DynamoDB: ${PN}-issues" "aws dynamodb describe-table --table-name ${PN}-issues --region $REGION"
check "DynamoDB: ${PN}-approvals" "aws dynamodb describe-table --table-name ${PN}-approvals --region $REGION"

AGENT_ID=$(aws bedrock-agent list-agents --region $REGION --query "agentSummaries[?contains(agentName,'${PN}')].agentId" --output text 2>/dev/null)
check "Bedrock Agent exists" "[ -n '$AGENT_ID' ]"
check "Bedrock Agent prepared" "aws bedrock-agent get-agent --agent-id $AGENT_ID --region $REGION --query 'agent.agentStatus' --output text 2>/dev/null | grep -q PREPARED"

KB_ID=$(aws bedrock-agent list-knowledge-bases --region $REGION --query "knowledgeBaseSummaries[?contains(name,'${PN}')].knowledgeBaseId" --output text 2>/dev/null)
check "Bedrock KB exists" "[ -n '$KB_ID' ]"
check "Bedrock KB active" "aws bedrock-agent get-knowledge-base --knowledge-base-id $KB_ID --region $REGION --query 'knowledgeBase.status' --output text 2>/dev/null | grep -q ACTIVE"

AOSS=$(aws opensearchserverless list-collections --region $REGION --query "collectionSummaries[?contains(name,'${PN}')].status" --output text 2>/dev/null)
check "AOSS collection active" "echo $AOSS | grep -q ACTIVE"

check "Lambda: ${PN}-agent-diagnose" "aws lambda get-function --function-name ${PN}-agent-diagnose --region $REGION"
check "Lambda: ${PN}-agent-tools" "aws lambda get-function --function-name ${PN}-agent-tools --region $REGION"
check "Lambda: ${PN}-get-issues" "aws lambda get-function --function-name ${PN}-get-issues --region $REGION"
check "Lambda: ${PN}-approvals" "aws lambda get-function --function-name ${PN}-approvals --region $REGION"

# ── STEP 4: CHAOS & API & UI ──
echo ""
echo "▶ STEP 4: CHAOS & API & UI"
check "Lambda: ${PN}-chaos-engine" "aws lambda get-function --function-name ${PN}-chaos-engine --region $REGION"
check "Lambda: ${PN}-patch-alertmanager" "aws lambda get-function --function-name ${PN}-patch-alertmanager --region $REGION"

API_ID=$(aws apigateway get-rest-apis --region $REGION --query "items[?contains(name,'${PN}')].id" --output text 2>/dev/null)
check "API Gateway exists" "[ -n '$API_ID' ]"
API_URL="https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod"
check "API /issues responds" "curl -sf ${API_URL}/issues"

CF_DOMAIN=$(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Origins.Items[0].DomainName,'${PN}-ui')].DomainName" --output text 2>/dev/null)
check "CloudFront exists" "[ -n '$CF_DOMAIN' ]"
check "UI loads" "curl -sf https://${CF_DOMAIN}/ | grep -q 'html'"

# AlertManager webhook
AM_CONFIG=$(kubectl get secret alertmanager-prometheus-kube-prometheus-alertmanager -n monitoring -o jsonpath='{.data.alertmanager\.yaml}' 2>/dev/null | base64 -d 2>/dev/null)
check "AlertManager webhook patched" "echo '$AM_CONFIG' | grep -q 'agent-diagnose'"

# ── END-TO-END TEST ──
echo ""
echo "▶ END-TO-END TEST"
echo "  Crashing SMF..."
kubectl scale deployment smf -n open5gs --replicas=0 2>/dev/null
sleep 45

check "Alert fired" "kubectl exec prometheus-prometheus-kube-prometheus-prometheus-0 -n monitoring -c prometheus -- sh -c 'wget -qO- \"http://localhost:9090/api/v1/rules?type=alert\"' 2>/dev/null | grep -q NFScaledToZero"

APPROVAL=$(aws dynamodb scan --table-name ${PN}-approvals --region $REGION --filter-expression '#s = :p' --expression-attribute-names '{\"#s\":\"status\"}' --expression-attribute-values '{\":p\":{\"S\":\"PENDING\"}}' --query 'Count' --output text 2>/dev/null)
check "Approval created with diagnosis" "[ '$APPROVAL' -gt 0 ] 2>/dev/null"

echo "  Restoring SMF..."
kubectl scale deployment smf -n open5gs --replicas=1 2>/dev/null
sleep 10
check "SMF restored" "kubectl get deploy smf -n open5gs --no-headers 2>/dev/null | grep -q '1/1'"

# ── SUMMARY ──
echo ""
echo "═══════════════════════════════════════════════════"
TOTAL=$((PASS + FAIL))
if [ $FAIL -eq 0 ]; then
  echo "✅ ALL $TOTAL CHECKS PASSED"
  echo "   Dashboard: https://${CF_DOMAIN}"
  echo "   API: ${API_URL}"
else
  echo "❌ $FAIL/$TOTAL CHECKS FAILED"
fi
echo "═══════════════════════════════════════════════════"
