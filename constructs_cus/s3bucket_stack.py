import yaml
from aws_cdk import Stack, RemovalPolicy, Duration, CfnOutput
from aws_cdk.aws_s3 import Bucket, BucketEncryption, BlockPublicAccess, LifecycleRule, BucketAccessControl
from aws_cdk.aws_iam import PolicyStatement, AccountRootPrincipal
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from constructs import Construct


class S3BucketStack(Construct):
    def __init__(self, scope: Construct, id: str, config: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Map string values in config to BucketAccessControl enum values
        access_control_mapping = {
            "PRIVATE": BucketAccessControl.PRIVATE,
            "PUBLIC_READ": BucketAccessControl.PUBLIC_READ,
            "PUBLIC_READ_WRITE": BucketAccessControl.PUBLIC_READ_WRITE,
            "AUTHENTICATED_READ": BucketAccessControl.AUTHENTICATED_READ,
            "BUCKET_OWNER_READ": BucketAccessControl.BUCKET_OWNER_READ,
            "BUCKET_OWNER_FULL_CONTROL": BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            "LOG_DELIVERY_WRITE": BucketAccessControl.LOG_DELIVERY_WRITE,
        }
        # Convert string to enum; use PRIVATE by default if access_control is invalid
        access_control = access_control_mapping.get(config["access_control"], BucketAccessControl.PRIVATE)

        # Create the S3 bucket using the mapped enum value
        s3_bucket = Bucket(
            self,
            "ConfiguredS3Bucket",
            bucket_name=config["bucket_name"],  
            versioned=config["versioned"],     
            block_public_access=BlockPublicAccess.BLOCK_ALL,  
            encryption=BucketEncryption.S3_MANAGED,          
            bucket_key_enabled=config["bucket_key_enabled"], 
            access_control=access_control,  # Pass the valid enum value
            removal_policy=RemovalPolicy.RETAIN if config["retain_on_delete"] else RemovalPolicy.DESTROY,
            lifecycle_rules=[
                LifecycleRule(
                    id="ExpireOldVersions",
                    noncurrent_version_expiration=Duration.days(config["lifecycle"]["noncurrent_version_expiration_days"])
                )
            ]
        )

        # Attach bucket policy dynamically
        bucket_policy = PolicyStatement(
            actions=config["bucket_policy"]["actions"], 
            resources=[f"{s3_bucket.bucket_arn}/*"],     
            principals=[AccountRootPrincipal()]         
        )
        s3_bucket.add_to_resource_policy(bucket_policy)

        # # Deploy initial content into the bucket
        # BucketDeployment(
        #     self,
        #     "SampleFileDeployment",
        #     sources=[Source.asset(config["file_upload"]["local_path"])],
        #     destination_bucket=s3_bucket
        # )

        # Output bucket information
        CfnOutput(self, "BucketArn", value=s3_bucket.bucket_arn, description="The ARN of the created S3 bucket")
        CfnOutput(self, "BucketWebsiteUrl", value=s3_bucket.bucket_website_url, description="The Website URL of the bucket for direct object access")