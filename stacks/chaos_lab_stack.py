"""Stack 4a: Chaos engine Lambda — crash-only, no diagnosis."""
import aws_cdk as cdk
from aws_cdk import aws_lambda as _lambda, aws_iam as iam
from constructs import Construct
import os

LAMBDA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lambda-src")


class ChaosLabStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str,
                 cluster_name: str, k8s_admin_role_arn: str,
                 agent_id: str, agent_alias_id: str,
                 approvals_table_name: str,
                 kubectl_layer,
                 config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        pn = config["project_name"]

        self.chaos_fn = _lambda.Function(self, "ChaosEngineFn",
            function_name=f"{pn}-chaos-engine",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="jitu_chaos_engine.lambda_handler",
            code=_lambda.Code.from_asset(os.path.join(LAMBDA_DIR, "chaos-engine")),
            timeout=cdk.Duration.seconds(120),
            memory_size=512,
            architecture=_lambda.Architecture.ARM_64,
            layers=[kubectl_layer],
            environment={
                "CLUSTER_NAME": cluster_name,
                "K8S_ROLE_ARN": k8s_admin_role_arn,
                "NAMESPACE": config["nf_namespace"],
                "AGENT_ID": agent_id,
                "AGENT_ALIAS_ID": agent_alias_id,
                "APPROVALS_TABLE": approvals_table_name,
            },
        )
        self.chaos_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"], resources=[k8s_admin_role_arn]))
        self.chaos_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["eks:DescribeCluster"], resources=["*"]))
        self.chaos_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeAgent"], resources=["*"]))
        self.chaos_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["lambda:InvokeFunction"],
            resources=[f"arn:aws:lambda:{cdk.Stack.of(self).region}:{cdk.Stack.of(self).account}:function:{pn}-chaos-engine"]))
