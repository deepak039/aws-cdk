from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
)
from constructs import Construct

class ALBStack(Stack):
    def __init__(self, scope: Construct,config:dict,vpc,asg, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Lookup VPC
       

        # IAM Role for EC2 instances
        # role = iam.Role(
        #     self, "ASGInstanceRole",
        #     assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        #     managed_policies=[
        #         iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
        #     ]
        # )

     

        # User data (optional): Install Node.js app on instance start
        # asg.add_user_data("""
        #     #!/bin/bash
        #     yum update -y
        #     curl -sL https://rpm.nodesource.com/setup_16.x | bash -
        #     yum install nodejs -y
        #     echo 'const http = require("http"); const server = http.createServer((req, res) => { res.writeHead(200, {"Content-Type": "text/plain"}); res.end("Hello from Node.js"); }); server.listen(3000);' > /home/ec2-user/app.js
        #     node /home/ec2-user/app.js &
        # """)

        # Create an ALB
        alb = elbv2.ApplicationLoadBalancer(
            self, "NodeJsLoadBalancer",
            vpc=vpc,
            internet_facing=True
        )

        listener = alb.add_listener(
            "Listener",
            port=80,
            open=True
        )

        # Add ASG instances as targets to the ALB
        listener.add_targets(
            "ApplicationFleet",
            port=3000,
            targets=[asg]
        )

        # Output the Load Balancer DNS name
        from aws_cdk import CfnOutput
        CfnOutput(self, "LoadBalancerDNS", value=alb.load_balancer_dns_name)