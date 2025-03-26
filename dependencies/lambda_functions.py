from aws_cdk import (
    Stack,
   
)

def addDynamoDBRole(lambda_role):
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:GetItem",           
                    "dynamodb:PutItem",           
                    "dynamodb:DeleteItem",        
                    "dynamodb:Query",             
                    "dynamodb:Scan",              
                ],
                resources=[dynamo_table.table_arn]  
            )
        )