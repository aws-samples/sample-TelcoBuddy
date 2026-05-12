"""Region-aware configuration for Telco Buddy CDK."""

# Bedrock model mapping — inference profiles per region
BEDROCK_MODELS = {
    "us-east-1": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "us-east-2": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "us-west-2": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "eu-west-1": "eu.anthropic.claude-sonnet-4-20250514-v1:0",
    "eu-central-1": "eu.anthropic.claude-sonnet-4-20250514-v1:0",
    "ap-southeast-1": "apac.anthropic.claude-sonnet-4-20250514-v1:0",
    "ap-northeast-1": "apac.anthropic.claude-sonnet-4-20250514-v1:0",
    "ap-south-1": "apac.anthropic.claude-sonnet-4-20250514-v1:0",
}

ECR_PUBLIC = "public.ecr.aws"

def get_bedrock_model(region: str, override: str = "auto") -> str:
    if override and override != "auto":
        return override
    # At synth time, region may be a CDK token — default to us inference profile
    if "${Token" in str(region) or region not in BEDROCK_MODELS:
        return "us.anthropic.claude-sonnet-4-20250514-v1:0"
    return BEDROCK_MODELS[region]

def get_image_uri(ecr_alias: str, repo: str, tag: str) -> str:
    return f"{ECR_PUBLIC}/{ecr_alias}/telco-buddy/{repo}:{tag}"
