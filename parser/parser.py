import os

import aws_cdk as cdk
from .utils.config_loader import ConfigLoader

from stacks.api_gateway_stack import ApiGatewayStack
from  stacks.lambda_stack import LambdaStack
from  stacks.vpc import VpcStack
from  stacks.security_groups import SecurityGroupStack
from  stacks.vpc_endpoints import  VpcEndpoint
from  stacks.public_route_table import  PublicRoute
from  stacks.private_route_table import  PrivateRoute
from  stacks.dynamoDB_stack import DynamoDBStack
from  stacks.rds_stack import RDSStack
from stacks.ec2_stack import Ec2Stack
from stacks.asg_stack import ASGStack
from stacks.alb_stack import ALBStack
from constructs import Construct
import yaml

class Parser:

    def __init__(self,app : Construct):
         self.resources = {}
         self.app = app
         self.function = {
            'lambdas' : self.createLambda,
            'api_gateways' : self.createApiGateway,
            'vpcs' : self.createVpc,
            'security_groups' : self.createSecurityGroups,
            'vpc_endpoints' : self.createVpcEndpoints,
            'dynamodb_tables': self.createDynamoDBTable,
            'rds_instances': self.createRDSInstance,
            'ec2':self.createEc2,
            'asg':self.createAsg,
            'alb':self.createAlb,
         }
    
        


    def createVpcEndpoints(self,config):
        vpc_endpoint = VpcEndpoint(scope = self.app,vpc=self.resources[config['vpc']].vpc,config=config)
        return vpc_endpoint

    def createSecurityGroups(self,config):
        
        sec_group = SecurityGroupStack(scope = self.app,vpc = self.resources[config['service']].vpc,config = config)
        return sec_group

    def createVpc(self,config):
        
        vpc_obj = VpcStack(scope = self.app,config = config)
        # public_route_table = PublicRoute(scope = self.app,vpc = vpc_obj.vpc,config = config)
        # private_route_table = PrivateRoute(scope = self.app,vpc = vpc_obj.vpc,config = config)
        return vpc_obj
    def createEc2(self,config):
        ec2Instance = Ec2Stack(scope = self.app,vpc = self.resources[config['vpc']].vpc,security_group = self.resources[config['security_group']].sg,config = config)
        return ec2Instance   
    
    def createAsg(self,config):
        asgg = ASGStack(scope = self.app,vpc = self.resources[config['vpc']].vpc,config = config)
        return asgg   
    
    def createAlb(self,config):
        alb=ALBStack(scope = self.app,vpc = self.resources[config['vpc']].vpc, asg=self.resources[config['asg']].asg,config = config)
        return alb
    
    def createLambda(self,config):
        lambda_func = LambdaStack(scope = self.app,vpc = self.resources[config['vpc']].vpc,security_group = self.resources[config['security_group']].sg,config = config)
        return lambda_func
        
    
    def createApiGateway(self,config : dict):
        
        if config['name'] not in self.resources:
            gateway = ApiGatewayStack(scope = self.app,lambda_stack = self.resources[config['lambdaname']],config = config)
            gateway.createEndpoints(self.resources[config['lambdaname']],config['routes'])
            return gateway
        else:
            self.resources[config['name']].createEndpoints(self.resources[config['lambdaname']],config['routes'])
            return self.resources[config['name']]

    def createDynamoDBTable(self, config):
        dynamo_db_stack = DynamoDBStack(scope=self.app, config=config)
        return dynamo_db_stack

    def createRDSInstance(self, config):
        rds_stack = RDSStack(
            scope=self.app, 
            resources=self.resources, 
            config=config
        )
        return rds_stack



    def run(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)
        file_path = os.path.join(base_path,"parser",'utils','config1.yaml')
        config = ConfigLoader.load_config(file_path)
        
        for key,val in config.items():
            
            for instance in config[key]:
                inst_obj = self.function[key](config = instance)
                self.resources[instance['name']] = inst_obj







