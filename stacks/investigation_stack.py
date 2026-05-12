"""Stack 3c: Configure agent-tools Lambda with EKS access."""
import aws_cdk as cdk
from aws_cdk import aws_iam as iam, aws_lambda as _lambda
from constructs import Construct


class InvestigationStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str,
                 vpc, cluster, agent_tools_fn: _lambda.IFunction,
                 k8s_admin_role_arn: str, eks_cluster_sg,
                 config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Add EKS env vars and permissions to agent-tools Lambda
        # (Lambda created in ai_engine_stack, configured here with EKS access)
        cfn_fn = agent_tools_fn.node.default_child
        cfn_fn.add_property_override("Environment.Variables.CLUSTER_NAME", cluster.cluster_name)
        cfn_fn.add_property_override("Environment.Variables.K8S_ROLE_ARN", k8s_admin_role_arn)
        cfn_fn.add_property_override("Environment.Variables.NAMESPACE", config["nf_namespace"])

        agent_tools_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"], resources=[k8s_admin_role_arn]))
        agent_tools_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["eks:DescribeCluster"], resources=["*"]))
