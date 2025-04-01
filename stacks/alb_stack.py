from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct

class ALBStack(Stack):
    def __init__(self, scope: Construct, config: dict, vpc=None, asg=None, **kwargs):
        super().__init__(scope, config["name"], **kwargs)
        self.name = config["name"]

        # Create an ALB
        self.alb = elbv2.ApplicationLoadBalancer(
            self, "NodeJsLoadBalancer",
            vpc=vpc,
            internet_facing=True,
             vpc_subnets=ec2.SubnetSelection(
        subnet_type=ec2.SubnetType.PUBLIC ),
        )

        self.listener = self.alb.add_listener(
            "Listener",
            port=80,
            open=True,
        )

        # Add ASG instances as targets to the ALB
        self.listener.add_targets(
            
            "ApplicationFleet",
            port=8080,  # App running on port 8080
            targets=[asg],
            protocol=elbv2.ApplicationProtocol.HTTP,
           
        )

        # Output the Load Balancer DNS name
        CfnOutput(self, "LoadBalancerDNS", value=self.alb.load_balancer_dns_name)