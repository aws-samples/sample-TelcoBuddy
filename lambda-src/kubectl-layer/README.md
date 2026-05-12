# kubectl Lambda Layer

Packages `kubectl` as a Lambda layer for `agent-tools` and `approvals` Lambdas.

The binary is not committed (large + frequently updated). Fetch before `cdk deploy`:

```bash
cd lambda-src/kubectl-layer
mkdir -p python
KUBECTL_VERSION="v1.31.0"   # match your EKS cluster version
curl -L "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
  -o python/kubectl
chmod +x python/kubectl
```
