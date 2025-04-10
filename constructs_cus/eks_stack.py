from aws_cdk import (
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct
from aws_cdk.lambda_layer_kubectl_v28 import KubectlV28Layer


class EksStack(Construct):
    def __init__(self, scope: Construct, config: dict, vpc=None, **kwargs):
        super().__init__(scope, config['name'], **kwargs)
        self.name = config['name']

        # Create EKS Cluster Role
        # Create EKS Cluster Role
        cluster_role = iam.Role(
            self,
            f"{config['name']}-cluster-role",
            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy"),
            ]
        )

        # Create EKS Node Role
        node_role = iam.Role(
            self,
            f"{config['name']}-node-role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSWorkerNodePolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKS_CNI_Policy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"),
            ]
        )

        # Create EKS Cluster
        self.cluster = eks.Cluster(
            self,
            config['name'],
            cluster_name=config['name'],
            vpc=vpc,
            vpc_subnets=[{"subnet_type": ec2.SubnetType.PRIVATE_WITH_EGRESS}],
            default_capacity=0,
            role=cluster_role,
            version=eks.KubernetesVersion.V1_28,
            kubectl_layer=KubectlV28Layer(self, "kubectl"),
            output_cluster_name=True,
            output_config_command=True,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
        )

        # Map admin IAM roles (passed in the config) to Kubernetes system:masters
        # This allows these roles to have full admin access via kubectl.
        if "admin_roles" in config:
            for admin_arn in config["admin_roles"]:
                # Import role by ARN; you can also create a new role if needed.
                admin_role = iam.Role.from_role_arn(
                    self, 
                    f"AdminRole-{admin_arn['arn'].split('/')[-1]}", 
                    admin_arn['arn']
                )
                self.cluster.aws_auth.add_masters_role(admin_role)

        # Add Node Groups if specified
        if 'node_groups' in config:
            for ng_config in config['node_groups']:
                self.cluster.add_nodegroup_capacity(
                    f"{ng_config['name']}-ng",
                    instance_types=[ec2.InstanceType(ng_config.get('instance_type', 't3.medium'))],
                    min_size=ng_config.get('min_size', 1),
                    max_size=ng_config.get('max_size', 3),
                    desired_size=ng_config.get('desired_size', 2),
                    node_role=node_role,
                )
                # Map the node IAM role so the nodes register properly.
                self.cluster.aws_auth.add_role_mapping(
                    node_role, 
                    groups=[], 
                    username="system:node:{{EC2PrivateDNSName}}"
                )

        # Add Fargate Profiles if specified
        if 'fargate_profiles' in config:
            for profile_config in config['fargate_profiles']:
                self.cluster.add_fargate_profile(
                    f"{profile_config['name']}-fp",
                    selectors=[{"namespace": profile_config.get('namespace', 'default')}],
                )

        # Install Helm Charts if specified
        if 'helm_charts' in config:
            for chart_config in config['helm_charts']:
                self.cluster.add_helm_chart(
                    chart_config['name'],
                    chart=chart_config['chart'],
                    repository=chart_config.get('repository', None),
                    namespace=chart_config.get('namespace', 'default'),
                    values=chart_config.get('values', {}),
                )

        # Add Kubernetes manifests if specified
        if 'manifests' in config:
            for manifest in config['manifests']:
                self.cluster.add_manifest(manifest['name'], manifest['definition'])
