# AWS CDK Infrastructure as Code Deployment Guide 🌟

This **Configuration-driven AWS Deployment Tool** empowers you to create your AWS infrastructure effortlessly by simply defining your requirements through a YAML configuration file (config.yaml). Whether you need networking, compute, or serverless components, this tool enables you to deploy a complete AWS environment using AWS CDK.

─────────────────────────
⏩ Overview
─────────────────────────

This deployment framework supports:

• Modular Infrastructure Setup – Define only the services you need.
• Comprehensive Service Coverage – VPCs, security groups, compute resources, databases, object storage, Kubernetes clusters, etc.
• Inline IAM Policies – Easily attach inline policies to resources (e.g., Lambda functions) for fine-grained access control.

─────────────────────────
🛠 Supported AWS Services
─────────────────────────
1. Networking & Security  
  • VPCs with customizable subnets  
  • Security Groups with detailed ingress/egress rules  
  • VPC Endpoints
2. Compute & Auto Scaling  
  • EC2 Instances  
  • Auto Scaling Groups (ASG)  
  • Application Load Balancers (ALB)
3. Serverless Components  
  • AWS Lambda Functions  
  • API Gateway Integration  
  • DynamoDB Tables
4. Storage & Database Services  
  • Amazon S3 Buckets  
  • RDS Instances
  • DynamoDB Tables
6. Containers & Orchestration  
  • Elastic Kubernetes Service (EKS)
7. IAM Inline Policies  
  • Easily attach inline IAM policies to resources such as Lambda functions

─────────────────────────
🚀 Quick Start
─────────────────────────
1. Create and Activate a Python Virtual Environment  
  (a) Linux/macOS:
```
    $ python -m venv .venv  
    $ source .venv/bin/activate
```

  (b) Windows:  
```
    > python -m venv .venv  
    > .venv\Scripts\activate
```

3. Install Dependencies
```
  $ pip install -r requirements.txt  
```


5. Install and Configure AWS CDK
```
  $ npm install -g aws-cdk  
  Make sure your AWS CLI is configured with:  
  $ aws configure
```  

6. Create your <--your_config-->.yaml according to the guides below.

7. Deploy Your Infrastructure
```
  $ cdk deploy -c config=<--your_config-->.yaml
```  

8. To clean up and delete resources when needed
```
  $ cdk destroy -c config=<--your_config-->.yaml
```

─────────────────────────
📚 Configuration Reference
─────────────────────────

► VPC & Subnets – Easy Networking Setup  
Define a Virtual Private Cloud along with subnets:


-----------------------------------------------------
```
vpcs:
  - name: "main-vpc"              # Required: VPC name
    cidr: "10.0.0.0/16"           # Required: CIDR range
    max_azs: 2                    # Optional: Maximum Availability Zones (defaults to 3)
    subnets:
      - name: "public"
        type: "PUBLIC"            # Options: PUBLIC, PRIVATE_WITH_EGRESS, PRIVATE_ISOLATED
        cidr_mask: 24
      - name: "private"
        type: "PRIVATE_WITH_EGRESS"
        cidr_mask: 24
```

• Use PUBLIC subnets for internet-facing resources such as ALBs.
• Use PRIVATE / ISOLATED subnets for databases and internal services.

► Security Groups – Firewall Configuration  
Manage traffic using finely tuned security group rules:
```
-----------------------------------------------------
security_groups:
  - name: "sec-group-1"                   # Required: Security group name
    description: "Default VPC SG"         # Optional: Description of the group
    service: "main-vpc"                   # Required: VPC reference
    allow_all_outbound: true              # Optional: Allow outbound traffic
    ingress_rules:                        # Required: List of inbound rules
      - cidr: "10.0.0.0/16"
        port: "ALL_TRAFFIC"               # Use ALL_TRAFFIC to allow all ports/protocols within VPC
        description: "Allow all VPC traffic"
      - protocol: "TCP"
        port: 80
        cidr: "0.0.0.0/0"
        description: "Allow HTTP traffic from anywhere"
```       

► VPC Endpoints – Private Connectivity  
Access AWS services privately using VPC endpoints:
-----------------------------------------------------
```
vpc_endpoints:
  - service: dynamodb
    name: "TestEndpoint"                  # User defined name for endpoint
    vpc: "main-vpc"
    subnets:
      - "PRIVATE_WITH_EGRESS"             # Use one or more subnet types
```       

► EC2 Instances – Virtual Machines  
Launch customizable compute instances:
-----------------------------------------------------
```
ec2:
  - name: "analytics-server"              # Unique instance identifier
    vpc: "main-vpc"                       # Required VPC reference
    instance_type: "t2.micro"             # Specify instance type
    volume_size: 20                       # Storage (GB)
    security_group: "sec-group-1"         # Associated security group
    key_name: "admin-key"                 # Optional SSH key pair for access
    user_data_path: "scripts/analytics.sh" # Startup script
```    

► Auto Scaling Groups (ASG) – Dynamic Compute Scaling  
Scale EC2 instances dynamically based on demand:
-----------------------------------------------------
```
asg:
  - name: "web-asg"
    vpc: "main-vpc"
    user_data_path: "scripts/init.sh"     # Optional: Bootstrapping script
    min: 1                                # Minimum number of instances
    max: 3                                # Maximum number of instances
    desired: 2                            # Desired count at launch
```

► Load Balancers (ALB) – Traffic Distribution  
Distribute traffic across multiple instances:
-----------------------------------------------------
```
alb:
  - name: "web-alb"
    vpc: "main-vpc"
    asg: "web-asg"                        # Attach an Auto Scaling Group for backends
```

► DynamoDB Tables – NoSQL Database  
Provision highly scalable, low-latency NoSQL tables:
-----------------------------------------------------
```
dynamodb:
  - name: "user-data-table"
    partition_key:
      name: "UserID"
      type: "string"
    sort_key:
      name: "Timestamp"
      type: "number"
    billing_mode: "PAY_PER_REQUEST"       # Optional: Billing mode options```
    
```
► AWS Lambda – Serverless Functions  
Deploy Lambda functions with optional VPC access and security groups:
-----------------------------------------------------
```
lambdas:
  - name: "lambda1"
    runtime: "python3.9"                  # Runtime environment: python, nodejs, etc.
    handler: "index.handler"              # Entry point function handler
    code_path: "lambda/lambda1"           # Local path to Lambda code
    vpc: "main-vpc"                       # Optional: Attach Lambda to VPC
    security_group: "sec-group-1"
    policy:                              # Attach inline IAM policies via references
      - "dynamoDB_Perm"
```
► API Gateway – Managed APIs  
Expose your Lambda functions via REST APIs:
-----------------------------------------------------
```
api_gateways:
  - name: "user-api"
    lambdaname: "lambda1"                 # Lambda function to integrate
    routes:
      - path: "/users"
        method: "GET"
    key: "apikey-users"                   # API key reference for securing endpoints
```

► S3 Buckets – Scalable Object Storage  
Define S3 buckets with lifecycle policies and versioning:
-----------------------------------------------------

```
s3_buckets:
  - name: "my-backup-bucket"
    bucket_name: "backup-data-storage"
    versioned: true                       # Ensure bucket versioning is enabled
    bucket_key_enabled: true              # Enhance security with bucket key enabled
    access_control: PRIVATE               # Specify access control (e.g., PRIVATE)
    retain_on_delete: true                # Retain bucket on stack deletion
    lifecycle:
      noncurrent_version_expiration_days: 90
    bucket_policy:
      actions:
        - "s3:GetObject"
        - "s3:PutObject"
```

► RDS – Relational Database Service  
Set up a relational database with backup and security configuration:
-----------------------------------------------------
```
rds:
  - name: "prod-db-instance"
    vpc: "main-vpc"
    security_group: "sec-group-1"         # Attach appropriate security group
    instance_type: "db.m4.large"
    engine: "mysql"                       # Options: mysql, postgres, maria_db, etc.
    database_name: "prod_db"
    master_username: "admin"
    master_password: "SuperSecret123!"     # Use strong passwords or secrets manager
    backup_retention_days: 7              # Optional: Automatic backup retention period
    deletion_protection: true             # Prevent accidental deletion
```

► EKS – Elastic Kubernetes Service  
Deploy scalable Kubernetes clusters with managed node groups:
-----------------------------------------------------
```
eks:
  - name: "web-cluster"
    vpc: "main-vpc"
    admin_roles:                          # IAM roles with admin access to the cluster
      - arn: "arn:aws:iam::123456789012:user/admin"
    node_groups:
      - name: "app-nodes"
        desired_size: 2
        min_size: 1
        max_size: 5
    # Advanced options: Endpoint configurations, Fargate profiles, Helm charts, etc.
```    
    

► IAM Permissions – Inline Policies for Fine-Grained Access Control  
Attach inline IAM policies to resources such as Lambda functions:
-----------------------------------------------------
```
iam_permissions:
  - name: "dynamoDB_Perm"               # Policy name for reference
    policies:
      - action:
          - "dynamodb:GetItem"
          - "dynamodb:PutItem"
          - "dynamodb:UpdateItem"
          - "dynamodb:DeleteItem"
          - "dynamodb:Query"
          - "dynamodb:Scan"
        resource: "*"                   # Optional: define specific ARNs if needed

Then reference the IAM policy within your Lambda configuration:
-----------------------------------------------------
lambdas:
  - name: "lambda1"
    runtime: "python3.9"
    handler: "index.handler"
    code_path: "lambda/lambda1"
    vpc: "main-vpc"
    security_group: "sec-group-1"
    policy:
      - "dynamoDB_Perm"               # Attach inline IAM policy by name
```        
        
        

─────────────────────────
🛠 Advanced Developer Notes
─────────────────────────
• Parameter Validation: Ensure your YAML configuration is consistent and all file paths (e.g., code_path, user_data_path) exist.
• Resource Naming: Use unique names within each service type to avoid conflicts.
• Security Best Practices:  
  – Limit security group ingress access to only necessary ports/services.  
  – Enable encryption and backups for databases and storage.  
  – Regularly review and update IAM policies.
• Extensibility: The configuration can be extended for additional services or advanced configurations as needed.

─────────────────────────
✨ Get Started Today!
─────────────────────────
With this configuration-driven approach, your AWS infrastructure is just one YAML file away. Customize your config.yaml, deploy using the AWS CDK, and manage a secure, scalable environment according to your needs.

Happy building and innovating on AWS!
