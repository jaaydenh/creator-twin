from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
import os

load_dotenv()

profile_arn = os.getenv("BEDROCK_INFERENCE_PROFILE_ARN")
region = os.getenv("AWS_DEFAULT_REGION")


model = ChatBedrockConverse(
    model=profile_arn,
    provider="anthropic",
    temperature=0.5,
    region_name=region
)
