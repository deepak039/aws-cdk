# AWS CDK Infrastructure as Code Project

A configuration-driven AWS infrastructure deployment tool. Pick the services you need and create your infrastructure!

## 🎯 Quick Start

1. Install prerequisites:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Create your config.yaml using the service blocks you need

3. Deploy

```
cdk deploy -c config=your-config.yaml --all
```

📚 Service Configuration Guide
Pick the services you need from below and add them to your config.yaml. Each service block can be used independently.

🌐 Networking (VPC)

```
vpcs:
  - name: "prod-vpc"        # Required: Your VPC name
    cidr: "10.0.0.0/16"    # Required: VPC CIDR range

```

🔒 Security Groups

```
security_groups:
  - name: "web-sg"                     # Required: Security group name
    service: "prod-vpc"                # Required: VPC name reference
    rules:                            # Required: At least one rule
      - port: 80
        source: "0.0.0.0/0"
        description: "HTTP access"
      - port: 443
        source: "0.0.0.0/0"
        description: "HTTPS access"
```

💻 EC2 Instances

```
ec2:
  - name: "web-server"                # Required: Instance name
    vpc: "prod-vpc"                   # Required: VPC name reference
    security_group: "web-sg"          # Required: Security group reference
    user_data_path: "scripts/init.sh" # Optional: Startup script
```


🔄 Auto Scaling Groupasg:

```
  - name: "web-asg"                   # Required: ASG name
    vpc: "prod-vpc"                   # Required: VPC name reference
    min: 1                           # Required: Minimum instances
    max: 3                           # Required: Maximum instances
    desired: 2                       # Required: Desired capacity
    user_data_path: "scripts/init.sh" # Optional: Startup script
```

⚖️ Load Balancer
```
alb:
  - name: "web-alb"                   # Required: ALB name
    vpc: "prod-vpc"                   # Required: VPC name reference
    asg: "web-asg"                    # Required: ASG name reference
```

🧮 DynamoDB Tables
```
dynamodb:
  - name: "users-table"              # Required: Table name
    partition_key:                   # Required: Primary key
      name: "userId"
      type: "string"                # Options: string, number, binary
    sort_key:                       # Optional: Sort key
      name: "timestamp"
      type: "number"
    billing_mode: "PAY_PER_REQUEST" # Optional: Defaults to PAY_PER_REQUEST
```

⚡ Lambda Functions

```
lambdas:
  - name: "process-data"             # Required: Function name
    runtime: "nodejs20.x"            # Required: Runtime
    handler: "index.handler"         # Required: Handler
    code_path: "./lambda/process"    # Required: Code location
    vpc: "prod-vpc"                  # Optional: VPC name reference
    security_group: "lambda-sg"      # Optional: Security group reference
```

🌐 API Gateway

```
api_gateways:
  - name: "api"                      # Required: API name
    lambdaname: "process-data"       # Required: Lambda reference
    routes:                         # Required: At least one route
      - path: "/users"
        method: "GET"
    key: "api-key-1"                # Required: API key name
```

🗄️ RDS Database

```
rds_instances:
  - name: "prod-db"                  # Required: Database name
    vpc: "prod-vpc"                  # Required: VPC name reference
    security_group: "db-sg"          # Required: Security group reference
    instance_type: "t3.micro"        # Required: Instance size
    engine: "mysql"                  # Required: Database engine
    engine_version: "8.0"            # Required: Engine version
    database_name: "myapp"           # Required: Database name
    master_username: "admin"         # Required: Master username
    port: 3306                      # Optional: Defaults to engine standard
    backup_retention_days: 7         # Optional: Defaults to 7
    deletion_protection: false       # Optional: Defaults to false
```

📋 Example Configurations
Web Application Stack

```
vpcs:
  - name: "web-vpc"
    cidr: "10.0.0.0/16"

security_groups:
  - name: "web-sg"
    service: "web-vpc"
    rules:
      - port: 80
        source: "0.0.0.0/0"
        description: "HTTP"

asg:
  - name: "web-asg"
    vpc: "web-vpc"
    min: 2
    max: 4
    desired: 2
    user_data_path: "scripts/web-init.sh"

alb:
  - name: "web-alb"
    vpc: "web-vpc"
    asg: "web-asg"
```

Serverless API Stack

```
dynamodb:
  - name: "users"
    partition_key:
      name: "userId"
      type: "string"

lambdas:
  - name: "api-handler"
    runtime: "nodejs20.x"
    handler: "index.handler"
    code_path: "./lambda/api"

api_gateways:
  - name: "users-api"
    lambdaname: "api-handler"
    routes:
      - path: "/users"
        method: "GET"
    key: "users-api-key"
```

⚠️ Important Notes
Only include services you need in your config

Names must be unique within each service type

When referencing other services (like VPC or security groups), use exact names

Ensure all referenced paths (user_data_path, code_path) exist

🔒 Security Best Practices
Use private subnets for internal resources

Limit security group access to necessary ports only

Enable backup and encryption for databases

Use API keys for API Gateway endpoints

Store sensitive data in AWS Secrets Manager

    
