# AWS CDK Infrastructure as Code Project

A configuration-driven AWS infrastructure deployment tool that allows users to provision AWS infrastructure using simple YAML configuration files. No AWS CDK coding is required to deploy resources.

## 🚀 Features

- Configuration-driven infrastructure deployment
- Infrastructure as Code using AWS CDK
- Modular and reusable service blocks
- Supports:
  - VPC
  - Security Groups
  - EC2
  - Auto Scaling Groups
  - Application Load Balancers
  - DynamoDB
  - Lambda
  - API Gateway
  - RDS
  - S3
  - EKS

---

## 🎯 Quick Start

### Prerequisites

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install pyyaml
pip install aws-cdk.lambda-layer-kubectl-v28
```

### Deploy Infrastructure

```bash
cdk bootstrap
cdk synth
cdk deploy
```

---

# Supported Resources

## 🌐 VPC

```yaml
vpcs:
  - name: "prod-vpc"
    cidr: "10.0.0.0/16"
```

---

## 🔒 Security Groups

```yaml
security_groups:
  - name: "web-sg"
    service: "prod-vpc"
    rules:
      - port: 80
        source: "0.0.0.0/0"
        description: "HTTP access"

      - port: 443
        source: "0.0.0.0/0"
        description: "HTTPS access"
```

---

## 💻 EC2 Instances

```yaml
ec2:
  - name: "web-server"
    vpc: "prod-vpc"
    security_group: "web-sg"
    user_data_path: "scripts/init.sh"
```

---

## 🔄 Auto Scaling Groups

```yaml
asg:
  - name: "web-asg"
    vpc: "prod-vpc"
    min: 1
    max: 3
    desired: 2
    user_data_path: "scripts/init.sh"
```

---

## ⚖️ Application Load Balancer

```yaml
alb:
  - name: "web-alb"
    vpc: "prod-vpc"
    asg: "web-asg"
```

---

## 🧮 DynamoDB

```yaml
dynamodb:
  - name: "users-table"
    partition_key:
      name: "userId"
      type: "string"

    sort_key:
      name: "timestamp"
      type: "number"

    billing_mode: "PAY_PER_REQUEST"
```

---

## ⚡ Lambda Functions

```yaml
lambdas:
  - name: "process-data"
    runtime: "nodejs20.x"
    handler: "index.handler"
    code_path: "./lambda/process"
    vpc: "prod-vpc"
    security_group: "lambda-sg"
```

---

## 🌐 API Gateway

```yaml
api_gateways:
  - name: "api"
    lambdaname: "process-data"

    routes:
      - path: "/users"
        method: "GET"

    key: "api-key-1"
```

---

## 🗄️ RDS

```yaml
rds_instances:
  - name: "prod-db"
    vpc: "prod-vpc"
    security_group: "db-sg"
    instance_type: "t3.micro"

    engine: "mysql"
    engine_version: "8.0"

    database_name: "myapp"
    master_username: "admin"

    port: 3306
    backup_retention_days: 7
    deletion_protection: false
```

---

# 📋 Example Configurations

## Web Application Stack

```yaml
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

---

## Serverless API Stack

```yaml
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

---

# 🔒 Security Best Practices

- Use private subnets for internal resources.
- Restrict security group access to required ports only.
- Enable encryption and backups for databases.
- Use API keys for API Gateway endpoints.
- Store secrets in AWS Secrets Manager.
- Follow the principle of least privilege for IAM roles.

---

# ⚠️ Important Notes

- Only define the services you need.
- Resource names should be unique.
- Service references must use exact names.
- Ensure referenced files and scripts exist.
- Validate YAML configuration before deployment.
