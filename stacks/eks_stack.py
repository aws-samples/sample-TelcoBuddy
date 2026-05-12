"""Stack 1b: EKS cluster, managed nodegroup, k8s-admin role, namespaces."""
import aws_cdk as cdk
from aws_cdk import aws_eks as eks, aws_ec2 as ec2, aws_iam as iam, aws_lambda as _lambda
from aws_cdk.lambda_layer_kubectl_v31 import KubectlV31Layer
import os
from constructs import Construct


class EksStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.IVpc, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        pn = config["project_name"]

        # K8s admin role — shared by all Lambdas that need kubectl
        self.k8s_admin_role = iam.Role(self, "K8sAdminRole",
            role_name=f"{pn}-k8s-admin",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("lambda.amazonaws.com"),
                iam.AccountRootPrincipal(),
            ),
        )
        self.k8s_admin_role.add_to_policy(iam.PolicyStatement(
            actions=["eks:DescribeCluster"], resources=["*"]))

        # EKS Cluster
        self.cluster = eks.Cluster(self, "Cluster",
            cluster_name=f"{pn}-5g-cluster",
            version=eks.KubernetesVersion.of(config.get("eks_version", "1.31")),
            vpc=vpc,
            default_capacity=0,  # We add nodegroup explicitly
            masters_role=self.k8s_admin_role,
            kubectl_layer=KubectlV31Layer(self, "KubectlLayer"),
        )

        # Map k8s-admin role to system:masters
        self.cluster.aws_auth.add_role_mapping(self.k8s_admin_role,
            groups=["system:masters"], username="k8s-admin")

        # Managed nodegroup
        self.cluster.add_nodegroup_capacity("DefaultCapacity",
            instance_types=[ec2.InstanceType(config.get("eks_node_type", "t3.medium"))],
            desired_size=config.get("eks_node_count", 2),
            min_size=1,
            max_size=config.get("eks_node_count", 2),
            disk_size=config.get("eks_disk_size", 20),
            ami_type=eks.NodegroupAmiType.AL2_X86_64,
        )

        # Cluster security group (for Lambda VPC access)
        self.cluster_sg = self.cluster.cluster_security_group

        # Namespaces
        self.nf_ns = self.cluster.add_manifest("NfNamespace", {
            "apiVersion": "v1", "kind": "Namespace",
            "metadata": {"name": config["nf_namespace"]}
        })
        self.monitoring_ns = self.cluster.add_manifest("MonitoringNamespace", {
            "apiVersion": "v1", "kind": "Namespace",
            "metadata": {"name": "monitoring"}
        })

        # Kubectl layer for Lambdas that need K8s access (ARM64)
        self.kubectl_layer = _lambda.LayerVersion(self, "KubectlPyLayer",
            code=_lambda.Code.from_asset(os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "lambda-src", "kubectl-layer")),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            compatible_architectures=[_lambda.Architecture.ARM_64],
            description="kubernetes client for Lambda (ARM64)",
        )

        # Outputs
        cdk.CfnOutput(self, "ClusterName", value=self.cluster.cluster_name)
        cdk.CfnOutput(self, "K8sAdminRoleArn", value=self.k8s_admin_role.role_arn)
