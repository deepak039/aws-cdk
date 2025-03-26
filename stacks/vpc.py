from aws_cdk.aws_ec2 import Vpc, SubnetConfiguration, SubnetType, IpAddresses
from aws_cdk import (
    Stack,
   
)
from constructs import Construct
class VpcStack(Stack):
    def __init__(self, scope: Construct,config:dict, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        
        self.vpc = Vpc(
            self,
            config['name'],
            ip_addresses=IpAddresses.cidr(config["cidr"]),
            max_azs=config["max_azs"],
            
            subnet_configuration=[
                SubnetConfiguration(
                name=subnet["name"],
                subnet_type=SubnetType[subnet["type"]],
                cidr_mask=subnet["cidr_mask"]
                )
            for subnet in config["subnets"]
            ]
        )