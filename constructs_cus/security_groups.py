from aws_cdk.aws_ec2 import SecurityGroup, Peer, Port
from aws_cdk import (
    Stack,
   
)
from constructs import Construct
class SecurityGroupStack(Construct):
    def __init__(self, scope: Construct,vpc,config:dict, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.sg = SecurityGroup(
          self,
          f"{config['name']}",
          vpc=vpc,  
          description=config.get("description"),  
          allow_all_outbound=config.get("allow_all_outbound")      
        )
    
        for rule in config["ingress_rules"]:
          self.sg.add_ingress_rule(
            Peer.ipv4(rule["cidr"]),
            Port.all_traffic() if rule["port"] == "ALL_TRAFFIC" else Port.tcp(int(rule["port"])),
            rule["description"]
          )
    