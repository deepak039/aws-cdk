from aws_cdk.aws_ec2 import GatewayVpcEndpointAwsService,InterfaceVpcEndpointAwsService
from aws_cdk import (
    Stack,
   
)
from constructs import Construct
class VpcEndpoint(Construct):
    def __init__(self, scope: Construct,vpc,config:dict, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        service_map = {
            "dynamodb": GatewayVpcEndpointAwsService.DYNAMODB,
            "s3": GatewayVpcEndpointAwsService.S3,
            "kinesis": InterfaceVpcEndpointAwsService.KINESIS_STREAMS,
            "ec2": InterfaceVpcEndpointAwsService.EC2,
            "secretsmanager": InterfaceVpcEndpointAwsService.SECRETS_MANAGER
        }
        self.endpoint = vpc.add_gateway_endpoint(
            config['name'],
            service=service_map[config['service']],
            subnets=[{"subnet_type": subnet_type} for subnet_type in config["subnets"]]
        )

