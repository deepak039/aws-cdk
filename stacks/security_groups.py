from aws_cdk.aws_ec2 import SecurityGroup, Peer, Port
from aws_cdk import (
    Stack,
   
)
from constructs import Construct
class SecurityGroupStack(Stack):
    def __init__(self, scope: Construct,vpc,config:dict, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.sg = SecurityGroup(
          self,
          f"{config['name']}",
          vpc=vpc,  # Explicitly pass the VPC here (ensure no duplicate vpc in `config`)
          description=config.get("description"),  # Safe access via .get()
          allow_all_outbound=config.get("allow_all_outbound")      # Default true if not provided
        )
    
        for rule in config["ingress_rules"]:
          self.sg.add_ingress_rule(
            Peer.ipv4(rule["cidr"]),
            Port.all_traffic() if rule["port"] == "ALL_TRAFFIC" else Port.tcp(int(rule["port"])),
            rule["description"]
          )
    