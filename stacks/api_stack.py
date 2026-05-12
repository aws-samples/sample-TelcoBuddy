"""Stack 4b: API Gateway — all routes wired to Lambdas."""
import aws_cdk as cdk
from aws_cdk import aws_apigateway as apigw, aws_lambda as _lambda, aws_iam as iam
from constructs import Construct
import os


class ApiStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str,
                 agent_diagnose_fn, issues_fn, approvals_fn, chaos_fn,
                 cluster_name: str, k8s_admin_role_arn: str,
                 kubectl_layer,
                 config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        pn = config["project_name"]

        self.api = apigw.RestApi(self, "Api",
            rest_api_name=f"{pn}-api",
            deploy_options=apigw.StageOptions(stage_name="prod"),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "x-api-key"],
            ),
        )

        # Lambda integrations
        diagnose_int = apigw.LambdaIntegration(agent_diagnose_fn)
        issues_int = apigw.LambdaIntegration(issues_fn)
        approvals_int = apigw.LambdaIntegration(approvals_fn)
        chaos_int = apigw.LambdaIntegration(chaos_fn)

        # Routes
        self.api.root.add_resource("agent-diagnose").add_method("POST", diagnose_int)
        self.api.root.add_resource("chat").add_method("POST", diagnose_int)
        self.api.root.add_resource("issues").add_method("GET", issues_int)
        self.api.root.add_resource("nf-status").add_method("GET", issues_int)

        approvals_res = self.api.root.add_resource("approvals")
        approvals_res.add_method("GET", approvals_int)
        approvals_res.add_method("POST", approvals_int)

        heal_mode = self.api.root.add_resource("heal-mode")
        heal_mode.add_method("GET", approvals_int)
        heal_mode.add_method("POST", approvals_int)

        chaos_res = self.api.root.add_resource("chaos")
        chaos_res.add_method("POST", chaos_int)
        self.api.root.add_resource("chaos-status").add_method("GET", chaos_int)
        self.api.root.add_resource("chaos-events").add_method("GET", chaos_int)

        self.api_url_output = cdk.CfnOutput(self, "ApiUrl", value=self.api.url,
            export_name=f"{pn}-api-url")
        self.api_id_output = cdk.CfnOutput(self, "ApiId", value=self.api.rest_api_id,
            export_name=f"{pn}-api-id")

        # ── Patch AlertManager with webhook URL (post-deploy) ──
        patch_fn = _lambda.Function(self, "PatchAlertmanagerFn",
            function_name=f"{pn}-patch-alertmanager",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=_lambda.Code.from_asset(os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "lambda-src", "patch-alertmanager")),
            timeout=cdk.Duration.seconds(60),
            memory_size=128,
            architecture=_lambda.Architecture.ARM_64,
            layers=[kubectl_layer],
        )
        patch_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["sts:AssumeRole"], resources=[k8s_admin_role_arn]))
        patch_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["eks:DescribeCluster"], resources=["*"]))

        from aws_cdk import CustomResource, custom_resources as cr
        patch_provider = cr.Provider(self, "PatchAlertmanagerProvider",
            on_event_handler=patch_fn)
        CustomResource(self, "PatchAlertmanager",
            service_token=patch_provider.service_token,
            properties={
                "ClusterName": cluster_name,
                "K8sRoleArn": k8s_admin_role_arn,
                "WebhookUrl": cdk.Fn.join("", [
                    "https://", self.api.rest_api_id,
                    ".execute-api.", cdk.Stack.of(self).region, ".amazonaws.com/prod/",
                    "agent-diagnose"
                ]),
                "Prefix": pn,
                "GroupWait": config.get("alertmanager_group_wait", "2s"),
                "GroupInterval": config.get("alertmanager_group_interval", "2s"),
                "RepeatInterval": config.get("alertmanager_repeat_interval", "5m"),
            })
