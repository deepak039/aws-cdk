from aws_cdk import Stack
from constructs import Construct

from aws_cdk.aws_apigateway import RestApi, LambdaIntegration, AuthorizationType,Deployment,Stage,ApiKey,UsagePlan,ThrottleSettings
from stacks.lambda_stack import LambdaStack


class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct,lambda_stack: LambdaStack,config : dict, **kwargs):
        super().__init__(scope, config['name'], **kwargs)

        
        self.api = RestApi(
            self,
            id = config['name'],
            rest_api_name=config['name'],
            description="API Gateway connected to Lambda",
        )

       
        


    def _resolve_authorization(self, auth_type: str):
       
           if auth_type.upper() == "IAM":
              return AuthorizationType.IAM
           elif auth_type.upper() == "COGNITO":
            return AuthorizationType.COGNITO
           else:
            return AuthorizationType.NONE   

    def createEndpoints(self,lambda_stack,endpoints,key):
        for endpoint in endpoints:
    
            resource = self.api.root.add_resource(endpoint["path"].strip("/"))
            resource.add_method(
                endpoint["method"].upper(),
               
                LambdaIntegration(lambda_stack.my_lambda),
                 api_key_required=True,
            )
       

        plan = self.api.add_usage_plan("UsagePlan",
                name="MyPlan",
            throttle=ThrottleSettings(
                rate_limit=10,
                burst_limit=2
            ),
            api_stages=[
            {
            "api": self.api,  
            "stage": self.api.deployment_stage  
            }
            ]
        )

        api_key = self.api.add_api_key(key)
        plan.add_api_key(api_key)