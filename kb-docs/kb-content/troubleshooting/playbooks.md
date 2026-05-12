# 5G Network Troubleshooting Playbooks

## 1. AMF Authentication Failure

### Symptoms
- UE registration fails
- CloudWatch logs show: "Authentication failed" or "AUSF unreachable"
- Dashboard shows AMF errors

### Diagnosis Steps

**Step 1: Check AMF Service Health**
```bash
aws ecs describe-services --cluster 5g-core --services amf --region us-east-1 --query 'services[0].[status,runningCount,desiredCount]'
```
- Expected: `["ACTIVE", 1, 1]`
- If runningCount < desiredCount → Check task failures

**Step 2: Check AMF Logs**
```bash
aws logs tail /aws/ecs/5g-core/amf --follow --region us-east-1 | grep -i "error\|fail\|auth"
```
- Look for: Connection errors, timeout errors, authentication failures

**Step 3: Verify AUSF Connectivity**
```bash
aws ecs describe-services --cluster 5g-core --services ausf --region us-east-1 --query 'services[0].[status,runningCount]'
```
- AUSF must be running for authentication
- Check security groups allow AMF → AUSF communication (port 29509)

**Step 4: Check Network Configuration**
```bash
aws ec2 describe-security-groups --group-ids sg-0f4583b2634337b22 --region us-east-1 --query 'SecurityGroups[0].IpPermissions[*].[FromPort,ToPort,IpProtocol]'
```
- Verify ports 29500-29599 are open (5G SBI)

### Common Causes & Solutions

| Cause | Solution | Time |
|-------|----------|------|
| AUSF service down | Restart AUSF service | 2 min |
| Network partition | Check security groups, verify connectivity | 5 min |
| Configuration mismatch | Verify AMF-AUSF configuration alignment | 10 min |
| Resource exhaustion | Scale AMF (increase CPU/memory) | 5 min |
| Database connectivity | Check MongoDB connection from AMF | 5 min |

### Resolution Commands

**Restart AMF:**
```bash
aws ecs update-service --cluster 5g-core --service amf --force-new-deployment --region us-east-1
```

**Scale AMF:**
```bash
aws ecs update-service --cluster 5g-core --service amf --desired-count 2 --region us-east-1
```

**Check MongoDB connectivity:**
```bash
aws ecs describe-services --cluster 5g-core-cluster --services mongodb --region us-east-1 --query 'services[0].[status,runningCount]'
```

### Prevention
- Enable CloudWatch alarms for AMF errors
- Implement health checks with automatic restart
- Monitor AUSF availability
- Set up service discovery for automatic failover

---

## 2. UPF High Latency

### Symptoms
- Data plane latency > 30ms
- Dashboard shows red latency indicators
- User experience: Slow data transfer
- CloudWatch metric: `UPF_DataPlaneLatency` elevated

### Diagnosis Steps

**Step 1: Check UPF Resource Utilization**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=upf Name=ClusterName,Value=5g-core \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-east-1
```
- If CPU > 80% → Resource bottleneck
- If CPU < 50% → Network or configuration issue

**Step 2: Check UPF Task Count**
```bash
aws ecs describe-services --cluster 5g-core --services upf --region us-east-1 --query 'services[0].[desiredCount,runningCount,pendingCount]'
```
- If runningCount < desiredCount → Tasks failing to start

**Step 3: Check Network Connectivity**
```bash
# Check if UPF has network access
aws ecs list-tasks --cluster 5g-core --service-name upf --region us-east-1 | jq -r '.taskArns[0]' | xargs -I {} aws ecs describe-tasks --cluster 5g-core --tasks {} --region us-east-1 --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text
```
- Verify ENI has proper routing

**Step 4: Check SMF-UPF Communication**
```bash
aws logs tail /aws/ecs/5g-core/upf --since 5m --region us-east-1 | grep -i "pfcp\|session\|error"
```
- Look for PFCP session establishment errors
- Check for packet drops or timeouts

### Common Causes & Solutions

| Cause | Solution | Time | Cost Impact |
|-------|----------|------|-------------|
| CPU bottleneck | Scale UPF horizontally (add tasks) | 3 min | +$30/month per task |
| Memory pressure | Increase task memory allocation | 5 min | +$15/month |
| Network congestion | Check cross-AZ traffic, use same AZ | 10 min | -$10/month (data transfer) |
| Insufficient bandwidth | Upgrade task vCPU (0.5 → 1.0) | 5 min | +$30/month |
| GTP-U tunnel issues | Verify security groups allow UDP 2152 | 5 min | $0 |

### Resolution Commands

**Scale UPF horizontally:**
```bash
aws ecs update-service --cluster 5g-core --service upf --desired-count 2 --region us-east-1
```

**Increase UPF resources (requires new task definition):**
```bash
# Get current task definition
aws ecs describe-task-definition --task-definition 5g-upf --region us-east-1 > /tmp/upf-task-def.json

# Edit: Change cpu from "512" to "1024", memory from "1024" to "2048"
# Register new version and update service
```

**Check security group for GTP-U:**
```bash
aws ec2 describe-security-groups --group-ids sg-0f4583b2634337b22 --region us-east-1 --query 'SecurityGroups[0].IpPermissions[?FromPort==`2152`]'
```

### Performance Targets

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| Latency | < 20ms | 20-30ms | > 30ms |
| CPU | 50-70% | 70-85% | > 85% |
| Memory | 60-80% | 80-90% | > 90% |
| Throughput | > 100 Mbps | 50-100 Mbps | < 50 Mbps |

### Prevention
- Enable auto-scaling based on CPU/throughput
- Set CloudWatch alarms for latency > 25ms
- Monitor bandwidth utilization
- Use Application Load Balancer for traffic distribution

---

## 3. MongoDB Connection Issues

### Symptoms
- NFs can't connect to MongoDB
- Logs show: "MongoNetworkError" or "Connection refused"
- Data persistence failures
- Dashboard shows database errors

### Diagnosis Steps

**Step 1: Check MongoDB Service Status**
```bash
aws ecs describe-services --cluster 5g-core-cluster --services mongodb --region us-east-1 --query 'services[0].[status,runningCount,desiredCount]'
```
- Expected: `["ACTIVE", 1, 1]`

**Step 2: Check MongoDB Logs**
```bash
aws logs tail /aws/ecs/5g-core-cluster/mongodb --follow --region us-east-1 | grep -i "error\|connection\|auth"
```
- Look for: Authentication errors, connection limits, resource issues

**Step 3: Verify Network Connectivity**
```bash
# Get MongoDB task IP
aws ecs list-tasks --cluster 5g-core-cluster --service-name mongodb --region us-east-1 | jq -r '.taskArns[0]' | xargs -I {} aws ecs describe-tasks --cluster 5g-core-cluster --tasks {} --region us-east-1 --query 'tasks[0].containers[0].networkInterfaces[0].privateIpv4Address'
```

**Step 4: Check Security Groups**
```bash
aws ec2 describe-security-groups --group-ids sg-0f4583b2634337b22 --region us-east-1 --query 'SecurityGroups[0].IpPermissions[?FromPort==`27017`]'
```
- Port 27017 must be open from NF security groups

### Common Causes & Solutions

| Cause | Solution | Time |
|-------|----------|------|
| MongoDB service down | Restart MongoDB service | 2 min |
| Connection limit reached | Increase MongoDB connections config | 5 min |
| Security group misconfigured | Add rule: Allow 27017 from NF SG | 3 min |
| Authentication failure | Verify MongoDB credentials in NF config | 10 min |
| Resource exhaustion | Scale MongoDB (increase memory) | 5 min |

### Resolution Commands

**Restart MongoDB:**
```bash
aws ecs update-service --cluster 5g-core-cluster --service mongodb --force-new-deployment --region us-east-1
```

**Check MongoDB resource usage:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=mongodb Name=ClusterName,Value=5g-core-cluster \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-east-1
```

**Add security group rule:**
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-0f4583b2634337b22 \
  --protocol tcp \
  --port 27017 \
  --source-group sg-0f4583b2634337b22 \
  --region us-east-1
```

### Prevention
- Implement connection pooling in NFs
- Set up MongoDB replica set for HA
- Monitor connection count and memory usage
- Enable CloudWatch alarms for MongoDB errors

---

## 4. Bedrock AI API Errors

### Symptoms
- AI slice creation fails
- Dashboard AI features unresponsive
- Logs show: "BedrockException" or "ThrottlingException"
- Response time > 5 seconds

### Diagnosis Steps

**Step 1: Check Bedrock AI Agent Service**
```bash
aws ecs describe-services --cluster 5g-core-cluster --services bedrock-ai-agent --region us-east-1 --query 'services[0].[status,runningCount,desiredCount]'
```

**Step 2: Check Bedrock API Logs**
```bash
aws logs tail /aws/ecs/5g-core-cluster/bedrock-ai-agent --follow --region us-east-1 | grep -i "bedrock\|error\|throttl"
```

**Step 3: Verify Internet Connectivity**
```bash
# Bedrock requires outbound HTTPS (443) access
# Check if task has NAT Gateway or public IP
aws ecs list-tasks --cluster 5g-core-cluster --service-name bedrock-ai-agent --region us-east-1 | jq -r '.taskArns[0]' | xargs -I {} aws ecs describe-tasks --cluster 5g-core-cluster --tasks {} --region us-east-1 --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text | xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} --query 'NetworkInterfaces[0].Association.PublicIp' --region us-east-1
```

**Step 4: Check Bedrock Service Quotas**
```bash
aws service-quotas get-service-quota \
  --service-code bedrock \
  --quota-code L-12345678 \
  --region us-east-1 2>/dev/null || echo "Check Bedrock quotas in console"
```

### Common Causes & Solutions

| Cause | Solution | Time | Cost |
|-------|----------|------|------|
| No internet access | Add NAT Gateway or VPC Endpoint | 10 min | +$32/month |
| Throttling (rate limit) | Implement exponential backoff | 5 min | $0 |
| Invalid API key/permissions | Verify IAM role has Bedrock permissions | 5 min | $0 |
| Model not available | Check model ID, use Claude 3 Sonnet | 2 min | $0 |
| Timeout | Increase timeout, optimize prompt | 5 min | $0 |

### Resolution Commands

**Check IAM role permissions:**
```bash
aws ecs describe-task-definition --task-definition bedrock-ai-agent --region us-east-1 --query 'taskDefinition.taskRoleArn' --output text | xargs -I {} aws iam get-role --role-name $(basename {}) --query 'Role.RoleName'
```

**Verify Bedrock permissions:**
```bash
# Role should have: bedrock:InvokeModel, bedrock:InvokeModelWithResponseStream
aws iam list-attached-role-policies --role-name <role-name> --region us-east-1
```

**Test Bedrock connectivity:**
```bash
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-sonnet-20240229-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"test"}]}' \
  --region us-east-1 \
  /tmp/bedrock-test.json
```

### Prevention
- Implement retry logic with exponential backoff
- Cache common AI responses
- Monitor Bedrock API call rate
- Set up CloudWatch alarms for throttling errors
- Use VPC Endpoint for Bedrock (if available)

---

## 5. ECS Task Startup Failures

### Symptoms
- Service shows: desiredCount > runningCount
- Tasks in STOPPED state
- Logs show: "ResourceInitializationError" or "CannotPullContainerError"
- New deployments fail

### Diagnosis Steps

**Step 1: Check Stopped Tasks**
```bash
aws ecs list-tasks --cluster 5g-core --desired-status STOPPED --region us-east-1 | jq -r '.taskArns[0]' | xargs -I {} aws ecs describe-tasks --cluster 5g-core --tasks {} --region us-east-1 --query 'tasks[0].[stoppedReason,containers[0].reason]'
```

**Step 2: Common Error Messages**

**Error: "ResourceInitializationError: failed to validate logger args"**
- **Cause**: No VPC Endpoint for CloudWatch Logs, no internet access
- **Solution**: Create VPC Endpoint or add NAT Gateway

**Error: "CannotPullContainerError: pull image manifest has been retried"**
- **Cause**: No VPC Endpoint for ECR, no internet access
- **Solution**: Create VPC Endpoints for ECR (API + DKR)

**Error: "Task failed to start: insufficient memory"**
- **Cause**: Task definition memory too low
- **Solution**: Increase memory allocation

**Step 3: Check Network Configuration**
```bash
aws ecs describe-services --cluster 5g-core --services amf --region us-east-1 --query 'services[0].networkConfiguration.awsvpcConfiguration'
```
- If `assignPublicIp: DISABLED` → Need VPC Endpoints or NAT Gateway

### Common Causes & Solutions

| Error | Cause | Solution | Time | Cost |
|-------|-------|----------|------|------|
| Logger validation failed | No CloudWatch Logs access | Create VPC Endpoint | 5 min | +$7.20/month |
| Cannot pull container | No ECR access | Create ECR VPC Endpoints | 5 min | +$14.40/month |
| Insufficient memory | Under-provisioned | Increase task memory | 5 min | +$15/month |
| Port conflict | Port already in use | Change port mapping | 5 min | $0 |
| IAM permissions | Missing execution role perms | Add ECR, CloudWatch policies | 5 min | $0 |

### Resolution Commands

**Create VPC Endpoint for CloudWatch Logs:**
```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-077cbf887617ead15 \
  --service-name com.amazonaws.us-east-1.logs \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-0ec0823d96fdea209 \
  --security-group-ids sg-0f4583b2634337b22 \
  --private-dns-enabled \
  --region us-east-1
```

**Create VPC Endpoints for ECR:**
```bash
# ECR API
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-077cbf887617ead15 \
  --service-name com.amazonaws.us-east-1.ecr.api \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-0ec0823d96fdea209 \
  --security-group-ids sg-0f4583b2634337b22 \
  --private-dns-enabled \
  --region us-east-1

# ECR DKR
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-077cbf887617ead15 \
  --service-name com.amazonaws.us-east-1.ecr.dkr \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-0ec0823d96fdea209 \
  --security-group-ids sg-0f4583b2634337b22 \
  --private-dns-enabled \
  --region us-east-1

# S3 Gateway (for ECR layers)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-077cbf887617ead15 \
  --service-name com.amazonaws.us-east-1.s3 \
  --vpc-endpoint-type Gateway \
  --route-table-ids rtb-XXXXXXXX \
  --region us-east-1
```

**Check IAM execution role:**
```bash
aws ecs describe-task-definition --task-definition 5g-amf --region us-east-1 --query 'taskDefinition.executionRoleArn' --output text | xargs -I {} aws iam get-role --role-name $(basename {})
```

### Prevention
- Always use VPC Endpoints for private subnets
- Test task definitions in dev before production
- Monitor task startup time
- Set up CloudWatch alarms for task failures
- Use proper IAM roles with least privilege

---

## Quick Reference: Diagnostic Commands

### Service Health Check
```bash
# All services status
for cluster in 5g-core 5g-core-cluster 5g-core-bedrock-cluster; do
  echo "=== $cluster ==="
  aws ecs list-services --cluster $cluster --region us-east-1 --query 'serviceArns[]' --output text | xargs -I {} basename {} | xargs -I {} aws ecs describe-services --cluster $cluster --services {} --region us-east-1 --query 'services[0].[serviceName,status,runningCount,desiredCount]' --output table
done
```

### View Recent Logs
```bash
aws logs tail /aws/ecs/5g-core/amf --since 10m --region us-east-1
```

### Check Resource Usage
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=upf Name=ClusterName,Value=5g-core \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum \
  --region us-east-1
```

### Network Connectivity Test
```bash
# Check if task has internet access
aws ecs list-tasks --cluster 5g-core --service-name amf --region us-east-1 | jq -r '.taskArns[0]' | xargs -I {} aws ecs describe-tasks --cluster 5g-core --tasks {} --region us-east-1 --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text | xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} --query 'NetworkInterfaces[0].[Association.PublicIp,PrivateIpAddress,SubnetId]' --region us-east-1
```

## Escalation Matrix

| Issue Severity | Response Time | Escalation Path |
|----------------|---------------|-----------------|
| Critical (service down) | 15 minutes | On-call engineer → Team lead → Manager |
| High (degraded performance) | 1 hour | On-call engineer → Team lead |
| Medium (intermittent issues) | 4 hours | On-call engineer |
| Low (minor issues) | Next business day | Team backlog |

## Contact Information

- **On-call Engineer**: Check PagerDuty/OpsGenie
- **AWS Support**: Enterprise support case
- **Bedrock Support**: AWS Bedrock team via support case
- **Network Team**: Internal escalation for VPC/networking issues
