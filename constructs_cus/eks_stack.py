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

        # kubectl_layer = eks.KubectlLayer(self, "KubectlLayer")

        # Create EKS Cluster
        self.cluster = eks.Cluster(
            self,
            config['name'],
            cluster_name=config['name'],
            vpc=vpc,
            vpc_subnets=[{"subnet_type": ec2.SubnetType.PRIVATE_WITH_EGRESS}],
            # version=eks.KubernetesVersion.of(config.get('version', 'auto')),
            default_capacity=config.get('default_capacity', 2),
            default_capacity_instance=ec2.InstanceType(config.get('instance_type', 't3.medium')),
            role=cluster_role,
            version=eks.KubernetesVersion.V1_28,
            kubectl_layer=KubectlV28Layer(self, "kubectl")
           
        )

        # Add Node Group if specified
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
