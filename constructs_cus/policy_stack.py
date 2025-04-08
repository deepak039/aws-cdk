
from aws_cdk import (
    Stack,
   
)
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy,PolicyStatement
from dependencies.lambda_functions import addDynamoDBRole 
class PolicyStack(Construct):
    def __init__(self, scope: Construct,config:dict, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.name = config['name']
        self.policies = []
        print(config)
        for policy in config['policies']:

            self.policies.append(
                PolicyStatement(
                    actions=policy['action'],
                    resources=["*"]  
                )
            )
        

    