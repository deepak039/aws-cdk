
from aws_cdk import (
    Stack,
   
)
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy,PolicyStatement
from dependencies.lambda_functions import addDynamoDBRole 
class LambdaStack(Construct):
    def __init__(self, scope: Construct,config:dict,permissions : dict,vpc = None,security_group = None, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.name = config['name']
        print(vpc,security_group)
        self.lambda_role = Role(
            self,
            "LambdaExecutionRole",  
            assumed_by=ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        
      
        self.lambda_role = Role(
            self,
            "AWSLambdaExecutionRole",
            assumed_by=ServicePrincipal("lambda.amazonaws.com"),
        )

        self.lambda_role.add_to_policy(
            PolicyStatement(
                actions=[
                    "ec2:CreateNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface"
                ],
                resources=["*"]  
            )
        )
        print(permissions)
        if 'policy' in config:
            for policy_name in config['policy']:
                for policy in permissions[policy_name].policies:

                    self.lambda_role.add_to_policy(
                        policy
                    )


        code = ''

        if config['file_type'] == 'zip':
            code = Code.from_asset(config["code"]) 
        else:
            # logic of container code
            pass

        
        self.my_lambda = Function(
            self,
            id = config['name'],
            runtime=self._resolve_runtime(config["runtime"]),  
            handler=config["handler"],
            code=code,  
            vpc = vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups = [security_group],
            role=self.lambda_role,
        )
           
    def _resolve_runtime(self, runtime: str):
        runtime_options = {
                "nodejs_18": Runtime.NODEJS_18_X,
                "nodejs_16": Runtime.NODEJS_16_X,
                "nodejs_14": Runtime.NODEJS_14_X,
                "nodejs_12": Runtime.NODEJS_12_X,  
                "nodejs_20": Runtime.NODEJS_20_X,

                "python_3_9": Runtime.PYTHON_3_9,
                "python_3_8": Runtime.PYTHON_3_8,
                "python_3_7": Runtime.PYTHON_3_7,  
                "java_11": Runtime.JAVA_11,
                "java_8": Runtime.JAVA_8,

                "dotnet_6": Runtime.DOTNET_6,
                "dotnet_5": Runtime.DOTNET_CORE_3_1,  
                "ruby_3_2": Runtime.RUBY_3_2,
                "ruby_2_7": Runtime.RUBY_2_7,
                "go_1_x": Runtime.GO_1_X,         
        }
        try:
            return runtime_options[runtime.lower()]
        except KeyError:
            raise ValueError(f"Unsupported runtime: {runtime}. Supported runtimes are: {list(runtime_options.keys())}")

    # def addPolicy(self,policies):
    #     lambda_role = self.my_lambda.role
        
    #     for policy in policies:
    #         print(policy)
    #         lambda_role.add_to_policy(
    #             policy
    #         )