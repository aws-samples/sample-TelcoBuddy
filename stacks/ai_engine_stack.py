"""Stack 3b: AOSS + Bedrock KB + Bedrock Agent + agent-diagnose Lambda."""
import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3, aws_iam as iam, aws_lambda as _lambda,
    aws_bedrock as bedrock, aws_opensearchserverless as aoss,
)
from constructs import Construct
from config import get_bedrock_model
import json, os

LAMBDA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lambda-src")


class AiEngineStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str,
                 issues_table, approvals_table,
                 cluster_name: str, k8s_admin_role_arn: str, nf_namespace: str,
                 kubectl_layer,
                 config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        pn = config["project_name"]
        region = cdk.Stack.of(self).region
        account = cdk.Stack.of(self).account
        model_id = get_bedrock_model(region, config.get("bedrock_model", "auto"))

        # ── S3 bucket for KB documents ──
        kb_bucket = s3.Bucket(self, "KbBucket",
            bucket_name=f"{pn}-kb-{account}",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # ── AOSS Collection ──
        collection_name = f"{pn}-kb"

        # Encryption policy
        aoss.CfnSecurityPolicy(self, "AossEncPolicy",
            name=f"{pn}-kb-enc", type="encryption",
            policy=json.dumps({"Rules": [{"ResourceType": "collection",
                "Resource": [f"collection/{collection_name}"]}], "AWSOwnedKey": True}))

        # Network policy — allow Bedrock service access
        aoss.CfnSecurityPolicy(self, "AossNetPolicy",
            name=f"{pn}-kb-net", type="network",
            policy=json.dumps([{"Rules": [
                {"ResourceType": "collection", "Resource": [f"collection/{collection_name}"]},
                {"ResourceType": "dashboard", "Resource": [f"collection/{collection_name}"]}
            ], "AllowFromPublic": False, "SourceServices": ["bedrock.amazonaws.com"]}]))

        # Collection
        collection = aoss.CfnCollection(self, "AossCollection",
            name=collection_name, type="VECTORSEARCH")
        collection.add_dependency(
            self.node.find_child("AossEncPolicy"))

        # ── IAM Roles ──
        # KB role — access AOSS + S3
        kb_role = iam.Role(self, "KbRole",
            role_name=f"{pn}-bedrock-kb-role",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
        )
        kb_role.add_to_policy(iam.PolicyStatement(
            actions=["aoss:APIAccessAll"], resources=[f"arn:aws:aoss:{region}:{account}:collection/*"]))
        kb_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetObject", "s3:ListBucket"],
            resources=[kb_bucket.bucket_arn, f"{kb_bucket.bucket_arn}/*"]))
        kb_role.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=[f"arn:aws:bedrock:{region}::foundation-model/*"]))

        # Agent role
        agent_role = iam.Role(self, "AgentRole",
            role_name=f"{pn}-bedrock-agent-role",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
        )
        agent_role.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
            resources=[f"arn:aws:bedrock:{region}::foundation-model/*",
                       f"arn:aws:bedrock:{region}:{account}:inference-profile/*",
                       f"arn:aws:bedrock:*::foundation-model/*",
                       "arn:aws:bedrock:*:*:inference-profile/*"]))
        agent_role.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:Retrieve"], resources=["*"]))

        # ── AOSS Index Lambda (created first so we can reference its role in access policy) ──
        index_fn = _lambda.Function(self, "AossIndexFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=_lambda.Code.from_asset(os.path.join(LAMBDA_DIR, "aoss-index")),
            timeout=cdk.Duration.seconds(900),
        )
        index_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["aoss:APIAccessAll"], resources=["*"]))
        index_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["aoss:BatchGetCollection"], resources=["*"]))

        # AOSS data access policy — must use Fn::Sub to embed role ARNs properly
        access_policy = aoss.CfnAccessPolicy(self, "AossAccessPolicy",
            name=f"{pn}-kb-access", type="data",
            policy=cdk.Fn.sub(json.dumps([{
                "Rules": [
                    {"ResourceType": "index", "Resource": [f"index/{collection_name}/*"],
                     "Permission": ["aoss:*"]},
                    {"ResourceType": "collection", "Resource": [f"collection/{collection_name}"],
                     "Permission": ["aoss:*"]},
                ],
                "Principal": ["${KbRoleArn}", "${IndexFnRoleArn}"],
            }]), {"KbRoleArn": kb_role.role_arn, "IndexFnRoleArn": index_fn.role.role_arn}))

        # ── Bedrock KB ──
        kb = bedrock.CfnKnowledgeBase(self, "Kb",
            name=f"{pn}-kb",
            role_arn=kb_role.role_arn,
            knowledge_base_configuration={
                "type": "VECTOR",
                "vectorKnowledgeBaseConfiguration": {
                    "embeddingModelArn": f"arn:aws:bedrock:{region}::foundation-model/{config['embed_model']}",
                },
            },
            storage_configuration={
                "type": "OPENSEARCH_SERVERLESS",
                "opensearchServerlessConfiguration": {
                    "collectionArn": collection.attr_arn,
                    "vectorIndexName": "bedrock-knowledge-base-default-index",
                    "fieldMapping": {
                        "vectorField": "bedrock-knowledge-base-default-vector",
                        "textField": "AMAZON_BEDROCK_TEXT_CHUNK",
                        "metadataField": "AMAZON_BEDROCK_METADATA",
                    },
                },
            },
        )
        kb.add_dependency(collection)

        # KB data source — S3
        data_source = bedrock.CfnDataSource(self, "KbDataSource",
            name=f"{pn}-kb-s3",
            knowledge_base_id=kb.attr_knowledge_base_id,
            data_source_configuration={
                "type": "S3",
                "s3Configuration": {"bucketArn": kb_bucket.bucket_arn},
            },
        )

        # Auto-trigger KB ingestion after data source creation
        from aws_cdk import custom_resources as cr
        cr.AwsCustomResource(self, "KbIngestion",
            on_create=cr.AwsSdkCall(
                service="@aws-sdk/client-bedrock-agent",
                action="StartIngestionJob",
                parameters={
                    "knowledgeBaseId": kb.attr_knowledge_base_id,
                    "dataSourceId": data_source.attr_data_source_id,
                },
                physical_resource_id=cr.PhysicalResourceId.of("kb-ingestion")),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(actions=["bedrock:StartIngestionJob"], resources=["*"])]))

        # ── AOSS Index Custom Resource ──
        from aws_cdk import CustomResource
        aoss_index = CustomResource(self, "AossIndex",
            service_token=index_fn.function_arn,
            properties={
                "Endpoint": collection.attr_collection_endpoint,
                "IndexName": "bedrock-knowledge-base-default-index",
                "CollectionName": f"{pn}-kb",
            })
        aoss_index.node.add_dependency(collection)
        aoss_index.node.add_dependency(access_policy)

        # KB must wait for AOSS index to exist
        kb.add_dependency(aoss_index.node.default_child)

        # ── Upload KB docs to S3 ──
        from aws_cdk import aws_s3_deployment as s3deploy
        kb_content_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kb-docs", "kb-content")
        if os.path.exists(kb_content_dir):
            s3deploy.BucketDeployment(self, "KbDocsUpload",
                sources=[s3deploy.Source.asset(kb_content_dir)],
                destination_bucket=kb_bucket,
            )

        # ── Agent Tools Lambda (for action group) ──
        self.agent_tools_fn = _lambda.Function(self, "AgentToolsFn",
            function_name=f"{pn}-agent-tools",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(os.path.join(LAMBDA_DIR, "agent-tools")),
            timeout=cdk.Duration.seconds(120),
            memory_size=256,
            architecture=_lambda.Architecture.ARM_64,
            layers=[kubectl_layer],
            environment={
                "CLUSTER_NAME": cluster_name,
                "K8S_ROLE_ARN": k8s_admin_role_arn,
                "NAMESPACE": nf_namespace,
            },
        )
        self.agent_tools_fn.grant_invoke(iam.ServicePrincipal("bedrock.amazonaws.com"))
        self.agent_tools_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"], resources=[k8s_admin_role_arn]))
        self.agent_tools_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["eks:DescribeCluster"], resources=["*"]))

        # Action group schema
        schema = json.load(open(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "kb-docs", "action-group-schema.json")))

        # ── Bedrock Agent ──
        agent_instruction = open(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "kb-docs", "agent-instruction.txt")).read().strip()

        self.agent = bedrock.CfnAgent(self, "Agent",
            agent_name=f"{pn}-5g-agent",
            agent_resource_role_arn=agent_role.role_arn,
            foundation_model=model_id,
            instruction=agent_instruction,
            knowledge_bases=[{
                "knowledgeBaseId": kb.attr_knowledge_base_id,
                "description": "5G/4G network knowledge base with 3GPP specs and troubleshooting playbooks",
                "knowledgeBaseState": "ENABLED",
            }],
            action_groups=[{
                "actionGroupName": f"{pn}-investigation-tools",
                "actionGroupExecutor": {"lambda": self.agent_tools_fn.function_arn},
                "functionSchema": schema,
            }],
            auto_prepare=True,
        )

        self.agent_alias = bedrock.CfnAgentAlias(self, "AgentAlias",
            agent_id=self.agent.attr_agent_id,
            agent_alias_name="prod",
        )

        # ── Agent Diagnose Lambda ──
        self.agent_diagnose_fn = _lambda.Function(self, "AgentDiagnoseFn",
            function_name=f"{pn}-agent-diagnose",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(os.path.join(LAMBDA_DIR, "agent-diagnose")),
            timeout=cdk.Duration.seconds(300),
            memory_size=512,
            environment={
                "AGENT_ID": self.agent.attr_agent_id,
                "AGENT_ALIAS_ID": self.agent_alias.attr_agent_alias_id,
                "ISSUES_TABLE": issues_table.table_name,
                "APPROVALS_TABLE": approvals_table.table_name,
                "HEAL_MODE": config["heal_mode"],
            },
        )
        issues_table.grant_read_write_data(self.agent_diagnose_fn)
        approvals_table.grant_read_write_data(self.agent_diagnose_fn)
        self.agent_diagnose_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeAgent"], resources=["*"]))

        # Outputs
        cdk.CfnOutput(self, "AgentId", value=self.agent.attr_agent_id)
        cdk.CfnOutput(self, "AgentAliasId", value=self.agent_alias.attr_agent_alias_id)
        cdk.CfnOutput(self, "KbId", value=kb.attr_knowledge_base_id)
        cdk.CfnOutput(self, "KbBucketName", value=kb_bucket.bucket_name)
