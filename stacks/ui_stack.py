"""Stack 4c: S3 + CloudFront UI with config.js injection."""
import aws_cdk as cdk
from aws_cdk import (aws_s3 as s3, aws_s3_deployment as s3deploy,
                     aws_cloudfront as cf, aws_cloudfront_origins as origins,
                     aws_lambda as _lambda, aws_iam as iam)
from constructs import Construct
import os


class UiStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, api_id: str,
                 config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        pn = config["project_name"]
        account = cdk.Stack.of(self).account
        region = cdk.Stack.of(self).region

        # S3 bucket for UI
        bucket = s3.Bucket(self, "UiBucket",
            bucket_name=f"{pn}-ui-{account}",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # CloudFront
        distribution = cf.Distribution(self, "UiDistribution",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            default_root_object="index.html",
        )

        # Deploy UI files
        ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
        deploy_ui = s3deploy.BucketDeployment(self, "DeployUi",
            sources=[s3deploy.Source.asset(ui_dir)],
            destination_bucket=bucket,
            distribution=distribution,
            prune=False,
        )

        # Deploy config.js via a custom resource that writes directly to S3
        # This avoids BucketDeployment's limitation with Fn::ImportValue tokens
        config_fn = _lambda.Function(self, "ConfigWriterFn",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=_lambda.Code.from_inline("""
import json, boto3, urllib.request
def handler(event, context):
    try:
        if event['RequestType'] == 'Delete':
            send(event, context, 'SUCCESS')
            return
        props = event['ResourceProperties']
        s3 = boto3.client('s3')
        content = f'window.__API_URL__ = "{props["ApiUrl"]}";'
        s3.put_object(Bucket=props['Bucket'], Key='config.js',
                      Body=content, ContentType='application/javascript')
        send(event, context, 'SUCCESS')
    except Exception as e:
        send(event, context, 'FAILED', str(e)[:200])

def send(event, context, status, reason=''):
    body = json.dumps({'Status': status,
        'Reason': reason or context.log_stream_name,
        'PhysicalResourceId': 'config-writer',
        'StackId': event['StackId'], 'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId']}).encode()
    urllib.request.urlopen(urllib.request.Request(
        event['ResponseURL'], data=body, method='PUT',
        headers={'Content-Type': '', 'Content-Length': str(len(body))}))
"""),
            timeout=cdk.Duration.seconds(30),
        )
        bucket.grant_put(config_fn)

        api_url = cdk.Fn.join("", [
            "https://", api_id,
            ".execute-api.", region, ".amazonaws.com/prod/"
        ])

        from aws_cdk import CustomResource
        deploy_config = CustomResource(self, "DeployConfig",
            service_token=config_fn.function_arn,
            properties={
                "Bucket": bucket.bucket_name,
                "ApiUrl": api_url,
                "Version": "2",
            })
        deploy_config.node.add_dependency(deploy_ui)

        cdk.CfnOutput(self, "DashboardUrl",
            value=f"https://{distribution.distribution_domain_name}")
        cdk.CfnOutput(self, "UiBucketName", value=bucket.bucket_name)
