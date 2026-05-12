# AWS Infrastructure Guide for 5G Network Functions

## ECS Fargate for 5G Network Functions

### Best Practices

**Resource Allocation:**
- AMF/SMF/NRF: 0.5 vCPU, 1GB RAM (control plane, low resource)
- UPF: 1-2 vCPU, 2-4GB RAM (data plane, high throughput)
- MongoDB: 1 vCPU, 2GB RAM (persistent storage)
- AI/Bedrock services: 0.5 vCPU, 1GB RAM (API calls)

**Networking:**
- Use private subnets with NAT Gateway for outbound connectivity
- Disable public IP assignment to save $3.60/month per service
- Use VPC Endpoints for AWS services (CloudWatch, S3, ECR) - $7.20/month total
- Security groups: Allow only required ports between NFs

**Cost Optimization:**
- Right-size tasks based on actual CPU/memory usage
- Use Fargate Spot for non-critical workloads (70% savings)
- Consolidate low-traffic services
- Monitor CloudWatch metrics to identify over-provisioned tasks

### 5G Network Function Deployment Patterns

**Control Plane (AMF, SMF, NRF, AUSF, UDM, PCF, NSSF):**
- Low latency requirements (5-15ms)
- Stateful - use ECS service discovery
- Scale based on registration/session count
- CPU: 0.25-0.5 vCPU, Memory: 512MB-1GB

**Data Plane (UPF):**
- High throughput requirements (100+ Mbps)
- Stateless - can scale horizontally
- Scale based on bandwidth utilization
- CPU: 1-2 vCPU, Memory: 2-4GB

**Support Services (MongoDB, API Gateway):**
- Persistent storage - use EFS or EBS
- Connection pooling for database
- CPU: 0.5-1 vCPU, Memory: 1-2GB

## CloudWatch Metrics Interpretation

### Key Metrics for 5G NFs

**ECS Task Metrics:**
- `CPUUtilization` > 80% → Scale up or right-size
- `MemoryUtilization` > 85% → Increase memory allocation
- `TaskCount` < DesiredCount → Check task failures

**Custom 5G Metrics:**
- `AMF_RegistrationLatency` < 10ms → Normal
- `SMF_SessionSetupLatency` < 15ms → Normal
- `UPF_DataPlaneLatency` < 20ms → Normal
- `UPF_Throughput` → Monitor against bandwidth limits

**Alert Thresholds:**
- Latency > 2x baseline → Investigate
- Error rate > 1% → Critical
- Task restart > 3/hour → Check logs

### CloudWatch Logs Analysis

**Common Error Patterns:**

1. **"ResourceInitializationError: failed to validate logger args"**
   - Cause: No VPC Endpoint for CloudWatch Logs
   - Solution: Create VPC Endpoint or add NAT Gateway

2. **"CannotPullContainerError"**
   - Cause: No internet access or ECR permissions
   - Solution: Check NAT Gateway, VPC Endpoint for ECR

3. **"Task failed to start"**
   - Cause: Insufficient resources or port conflicts
   - Solution: Check task definition, security groups

4. **MongoDB connection errors**
   - Cause: Network connectivity or authentication
   - Solution: Verify security groups, connection strings

## VPC Networking for 5G Workloads

### Network Architecture

**Recommended Setup:**
```
VPC (10.0.0.0/16)
├── Public Subnets (10.0.1.0/24, 10.0.2.0/24)
│   └── NAT Gateway (for outbound traffic)
├── Private Subnets (10.0.10.0/24, 10.0.11.0/24)
│   └── ECS Tasks (5G NFs)
└── VPC Endpoints
    ├── CloudWatch Logs ($7.20/month)
    ├── ECR API + DKR ($14.40/month)
    └── S3 Gateway (Free)
```

**Security Groups:**
- Control Plane SG: Allow 5G SBI ports (29500-29599)
- Data Plane SG: Allow GTP-U (2152), PFCP (8805)
- MongoDB SG: Allow 27017 from NFs only
- Bedrock SG: Allow HTTPS (443) outbound

**Cost Optimization:**
- Use S3 Gateway Endpoint (free) instead of Interface Endpoint
- Single NAT Gateway for all AZs (if HA not critical)
- VPC Endpoints only for high-traffic services

### Inter-NF Communication

**Service Discovery:**
- Use ECS Service Discovery (Cloud Map)
- DNS names: `amf.5g-core.local`, `smf.5g-core.local`
- Automatic health checks and failover

**Load Balancing:**
- Internal ALB for HTTP-based NFs (AMF, SMF SBI)
- Direct task-to-task for GTP-U (UPF)

## Auto-Scaling Policies

### Target Tracking Scaling

**Control Plane (AMF, SMF):**
```yaml
Metric: CPUUtilization
Target: 70%
Scale-out cooldown: 60s
Scale-in cooldown: 300s
Min: 1, Max: 5
```

**Data Plane (UPF):**
```yaml
Metric: Custom - UPF_Throughput
Target: 80% of max bandwidth
Scale-out cooldown: 30s
Scale-in cooldown: 600s
Min: 2, Max: 10
```

### Step Scaling (Advanced)

**For burst traffic:**
- +50% utilization → Add 1 task
- +80% utilization → Add 2 tasks
- +100% utilization → Add 3 tasks

## Cost Optimization Strategies

### Immediate Savings

1. **Disable Public IPs** → Save $3.60/month per service
   - 33 services × $3.60 = $118.80/month saved
   - Use VPC Endpoints instead

2. **Right-size Tasks** → Save 30-50%
   - Monitor actual CPU/memory usage
   - Reduce over-provisioned resources
   - Estimated: $200/month saved

3. **Consolidate Services** → Save 20-30%
   - Combine low-traffic NFs in single task
   - Use sidecar pattern
   - Estimated: $100/month saved

### Long-term Optimization

4. **Use Fargate Spot** → Save 70%
   - For dev/test environments
   - For stateless workloads (UPF)

5. **Reserved Capacity** → Save 30-50%
   - For stable production workloads
   - 1-year or 3-year commitment

6. **Graviton2 (ARM)** → Save 20%
   - If containers support ARM architecture

## Troubleshooting Quick Reference

### Task Won't Start

**Check:**
1. CloudWatch Logs for error messages
2. Task definition: CPU/memory limits
3. Security groups: Required ports open
4. Subnets: Internet access (NAT or IGW)
5. IAM roles: Task execution role permissions

### High Latency

**Check:**
1. CPU/Memory utilization → Scale if > 80%
2. Network connectivity → Check security groups
3. Database connections → Check MongoDB performance
4. Cross-AZ traffic → Keep NFs in same AZ

### Connection Failures

**Check:**
1. Security groups: Source/destination rules
2. Service discovery: DNS resolution
3. Health checks: Task health status
4. Network ACLs: Subnet-level rules

### Cost Spike

**Check:**
1. Task count: Unexpected scaling
2. Data transfer: Cross-region or internet egress
3. CloudWatch Logs: Excessive logging
4. NAT Gateway: Data processing charges

## AWS Service Integration

### Bedrock AI Integration

**Best Practices:**
- Use VPC Endpoint for Bedrock (if available in region)
- Otherwise, use NAT Gateway for outbound HTTPS
- Cache responses to reduce API calls
- Implement retry logic with exponential backoff
- Monitor `bedrock:InvokeModel` CloudWatch metrics

**Cost:**
- Claude 3 Sonnet: $3 per 1M input tokens, $15 per 1M output tokens
- Typical 5G query: 500 input + 1000 output tokens = $0.017 per query

### S3 for Logs and Data

**Best Practices:**
- Use S3 Gateway Endpoint (free)
- Enable S3 Intelligent-Tiering for cost optimization
- Set lifecycle policies: Delete logs after 90 days
- Use S3 Select for log analysis (cheaper than downloading)

### CloudWatch Optimization

**Cost Reduction:**
- Use VPC Endpoint for Logs ($7.20/month vs data transfer costs)
- Reduce log verbosity in production
- Use metric filters instead of storing all logs
- Set log retention: 7 days for debug, 30 days for production

## Performance Benchmarks

### Expected Latencies (AWS ECS Fargate)

- **AMF Registration**: 5-10ms (normal), >15ms (investigate)
- **SMF Session Setup**: 8-15ms (normal), >20ms (investigate)
- **UPF Data Plane**: 10-20ms (normal), >30ms (investigate)
- **NRF Service Discovery**: 3-8ms (normal), >12ms (investigate)
- **MongoDB Query**: 5-15ms (normal), >25ms (investigate)
- **Bedrock AI Response**: 1-3s (normal), >5s (investigate)

### Throughput Benchmarks

- **UPF (0.5 vCPU)**: 50-100 Mbps
- **UPF (1 vCPU)**: 100-200 Mbps
- **UPF (2 vCPU)**: 200-500 Mbps

### Resource Utilization Baselines

- **Control Plane NFs**: 20-40% CPU, 40-60% Memory (normal)
- **Data Plane (UPF)**: 50-70% CPU, 60-80% Memory (normal)
- **MongoDB**: 30-50% CPU, 70-85% Memory (normal)

## Security Best Practices

### Network Security

1. **Principle of Least Privilege**
   - Security groups: Only required ports
   - IAM roles: Minimum permissions
   - VPC: Private subnets for all NFs

2. **Encryption**
   - TLS for all inter-NF communication
   - Encryption at rest for MongoDB (EBS encryption)
   - KMS for sensitive data

3. **Monitoring**
   - VPC Flow Logs for network traffic analysis
   - CloudTrail for API call auditing
   - GuardDuty for threat detection

### Compliance

- **Data Residency**: Keep all data in required region
- **Audit Logging**: Enable CloudTrail, CloudWatch Logs
- **Access Control**: Use IAM roles, not access keys
- **Encryption**: Enable for all data at rest and in transit

## Quick Commands

### Check Service Health
```bash
aws ecs describe-services --cluster 5g-core --services amf smf upf --region us-east-1 --query 'services[*].[serviceName,status,runningCount,desiredCount]' --output table
```

### View Task Logs
```bash
aws logs tail /aws/ecs/5g-core/amf --follow --region us-east-1
```

### Check Task Resource Usage
```bash
aws cloudwatch get-metric-statistics --namespace AWS/ECS --metric-name CPUUtilization --dimensions Name=ServiceName,Value=amf Name=ClusterName,Value=5g-core --start-time 2026-02-25T00:00:00Z --end-time 2026-02-25T23:59:59Z --period 3600 --statistics Average --region us-east-1
```

### List Public IPs (for cost audit)
```bash
aws ecs list-tasks --cluster 5g-core --region us-east-1 | jq -r '.taskArns[]' | xargs -I {} aws ecs describe-tasks --cluster 5g-core --tasks {} --region us-east-1 --query 'tasks[*].attachments[0].details[?name==`networkInterfaceId`].value' --output text | xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} --query 'NetworkInterfaces[*].Association.PublicIp' --output text
```

### Create VPC Endpoint for CloudWatch Logs
```bash
aws ec2 create-vpc-endpoint --vpc-id vpc-YOUR_VPC_ID --service-name com.amazonaws.us-east-1.logs --vpc-endpoint-type Interface --subnet-ids subnet-YOUR_SUBNET --security-group-ids sg-YOUR_SG --private-dns-enabled --region us-east-1
```

## Summary

**Key Takeaways:**
1. Use private subnets + VPC Endpoints for cost optimization
2. Right-size tasks based on actual usage (monitor CloudWatch)
3. Implement auto-scaling for dynamic workloads
4. Monitor latency and throughput against baselines
5. Follow security best practices (least privilege, encryption)

**Cost Optimization Priority:**
1. Disable public IPs → $118/month saved
2. Right-size tasks → $200/month saved
3. Consolidate services → $100/month saved
**Total potential savings: $418/month (36% reduction)**
