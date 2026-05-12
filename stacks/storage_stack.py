"""Stack 3a: DynamoDB tables + get-issues Lambda + approvals Lambda."""
import aws_cdk as cdk
from aws_cdk import (aws_dynamodb as ddb, aws_lambda as _lambda, aws_iam as iam)
from constructs import Construct
import os

LAMBDA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lambda-src")


class StorageStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, config: dict,
                 cluster_name: str, k8s_admin_role_arn: str,
                 kubectl_layer, **kwargs):
        super().__init__(scope, id, **kwargs)

        pn = config["project_name"]

        # DynamoDB tables
        self.issues_table = ddb.Table(self, "IssuesTable",
            table_name=f"{pn}-issues",
            partition_key=ddb.Attribute(name="issue_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        self.approvals_table = ddb.Table(self, "ApprovalsTable",
            table_name=f"{pn}-approvals",
            partition_key=ddb.Attribute(name="approval_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Kubectl layer passed from EKS stack
        self.kubectl_layer = kubectl_layer

        # Common env for K8s-aware Lambdas
        k8s_env = {
            "CLUSTER_NAME": cluster_name,
            "K8S_ROLE_ARN": k8s_admin_role_arn,
            "ISSUES_TABLE": self.issues_table.table_name,
            "APPROVALS_TABLE": self.approvals_table.table_name,
        }

        # Get Issues Lambda
        self.get_issues_fn = _lambda.Function(self, "GetIssuesFn",
            function_name=f"{pn}-get-issues",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="get_issues.lambda_handler",
            code=_lambda.Code.from_asset(os.path.join(LAMBDA_DIR, "get-issues")),
            timeout=cdk.Duration.seconds(30),
            memory_size=256,
            environment=k8s_env,
        )
        self.issues_table.grant_read_data(self.get_issues_fn)
        self.approvals_table.grant_read_data(self.get_issues_fn)
        self.get_issues_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["eks:DescribeCluster"], resources=["*"]))
        self.get_issues_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"], resources=[k8s_admin_role_arn]))

        # Approvals Lambda (reads/writes both tables + kubectl for healing)
        self.approvals_fn = _lambda.Function(self, "ApprovalsFn",
            function_name=f"{pn}-approvals",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="telco_buddy_approvals.lambda_handler",
            code=_lambda.Code.from_asset(os.path.join(LAMBDA_DIR, "approvals")),
            timeout=cdk.Duration.seconds(30),
            memory_size=256,
            environment=k8s_env,
            layers=[self.kubectl_layer] if self.kubectl_layer else [],
            architecture=_lambda.Architecture.ARM_64,
        )
        self.issues_table.grant_read_write_data(self.approvals_fn)
        self.approvals_table.grant_read_write_data(self.approvals_fn)
        # Allow assuming k8s-admin role for healing
        self.approvals_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"], resources=[k8s_admin_role_arn]))
        self.approvals_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["eks:DescribeCluster"], resources=["*"]))
