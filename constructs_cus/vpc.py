from aws_cdk.aws_ec2 import Vpc, SubnetConfiguration, SubnetType, IpAddresses
from aws_cdk import (
    Stack,
    Tags,
)
from constructs import Construct
class VpcStack(Construct):
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
        Tags.of(self.vpc).add("Name", config['name'])
         
        print(self.vpc.public_subnets)
        print(self.vpc.private_subnets)
        for subnet_config in config["subnets"]:
            print(subnet_config)
            if subnet_config["type"] == "PUBLIC":

                matching_subnets = [
                    subnet
                    for subnet in self.vpc.public_subnets
                    
                ]
                for subnet in matching_subnets:
                    print("public")
                    Tags.of(subnet).add("Name", subnet_config["name"])

            if subnet_config["type"] == "PRIVATE_WITH_EGRESS":
                
                matching_subnets = [
                    subnet
                    for subnet in self.vpc.private_subnets
                    
                ]
                for subnet in matching_subnets:
                    print("private")
                    Tags.of(subnet).add("Name", subnet_config["name"])

            if subnet_config["type"] == "PRIVATE_ISOLATED":
               
                matching_subnets = [
                    subnet
                    for subnet in self.vpc.isolated_subnets
                    
                ]
                for subnet in matching_subnets:
                    Tags.of(subnet).add("Name", subnet_config["name"])
