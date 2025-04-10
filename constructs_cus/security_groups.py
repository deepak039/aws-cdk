# AWS CDK Security Group Stack
#
# This module creates an AWS Security Group with configurable ingress rules.
#
# Example Usage:
"""
security_groups:
  name: my-security-group
  description: Security group for web servers 
  service:vpc
  allow_all_outbound: true
  ingress_rules:
    - protocol: tcp
      port: "80"
      cidr: 0.0.0.0/0
      description: Allow HTTP from anywhere
    - protocol: tcp 
      port: "443"
      cidr: 10.0.0.0/16
      description: Allow HTTPS from VPC
    - port: ALL_TRAFFIC
      cidr: 172.16.0.0/16
      description: Allow all traffic from specific network

"""

# Create the security group
# security_group = SecurityGroupStack(self, vpc, sg_config)
from aws_cdk.aws_ec2 import SecurityGroup, Peer, Port
from aws_cdk import (
    Stack,
   
)
from constructs import Construct
class SecurityGroupStack(Construct):
    def __init__(self, scope: Construct,vpc,config:dict, **kwargs):
        """
        Initialize Security Group Stack
        
        Args:
            scope: CDK Construct scope
            vpc: VPC to create the security group in
            config: Dictionary containing security group configuration
                Required keys:
                - name: Name of the security group
                - description: Security group description
                - allow_all_outbound: Boolean to allow all outbound traffic
                - ingress_rules: List of ingress rule dictionaries with:
                    - protocol: Protocol (tcp/udp), defaults to tcp
                    - port: Port number or "ALL_TRAFFIC"
                    - cidr: CIDR range for rule
                    - description: Rule description
        """
        super().__init__(scope, config['name'], **kwargs)
        self.sg = SecurityGroup(
          self,
          f"{config['name']}",
          vpc=vpc,  
          security_group_name=config.get("name"),
          description=config.get("description"),  
          allow_all_outbound=config.get("allow_all_outbound")      
        )
    
        for rule in config["ingress_rules"]:
          protocol = rule.get("protocol", "tcp").lower()
          port = Port.all_traffic() if rule["port"] == "ALL_TRAFFIC" else getattr(Port, protocol)(int(rule["port"]))
          self.sg.add_ingress_rule(
            Peer.ipv4(rule["cidr"]),
            port,
            rule["description"]
          )
    
