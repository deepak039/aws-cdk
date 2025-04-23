from aws_cdk import (
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct
from aws_cdk.lambda_layer_kubectl_v28 import KubectlV28Layer


class EksStack(Construct):
    def __init__(self, scope: Construct, config: dict, vpc=None, **kwargs):
        """
        Constructor for creating an EKS stack with configurable options.

        Args:
            scope (Construct): The scope of the stack.
            config (dict): Configuration dictionary that defines cluster options, node groups, Helm charts, etc.
            vpc: VPC object to deploy the cluster in (optional). If none is provided, auto-create one.
            **kwargs: Additional arguments for customization.

            Minimum Parameters Use Case

            name: "basic-eks-cluster"
            admin_roles:
              - arn: "arn:aws:iam::123456789012:role/AdminRole"
            node_groups:
             - name: "default-node-group"
            min_size: 1
            max_size: 3
            desired_size: 2


            Maximum Parameters Use Case 
            
            name: "advanced-eks-cluster"
            endpoint_access: PUBLIC_AND_PRIVATE
            admin_roles:
               - arn: "arn:aws:iam::123456789012:role/AdminRole1"
               - arn: "arn:aws:iam::123456789012:role/AdminRole2"
            node_groups:
            - name: "compute-node-group"
                instance_type: "c5.large"
                min_size: 3
                max_size: 10
                desired_size: 5
            - name: "gpu-node-group"
                instance_type: "p3.large"
                min_size: 1
                max_size: 5
                desired_size: 2
            fargate_profiles:
            - name: "fargate-apps-profile"
                namespace: "apps"
            helm_charts:
            - name: "prometheus"
                chart: "prometheus-community/prometheus"
                repository: "https://prometheus-community.github.io/helm-charts"
                namespace: "monitoring"
                values:
                service:
                    type: "ClusterIP"
                pushgateway:
                    enabled: false
            - name: "nginx-ingress"
                chart: "ingress-nginx/ingress-nginx"
                repository: "https://kubernetes.github.io/ingress-nginx"
                namespace: "ingress-nginx"
                values:
                controller:
                    replicaCount: 2
            manifests:
            - name: "namespace-apps"
                definition:
                apiVersion: v1
                kind: Namespace
                metadata:
                    name: "apps"
            - name: "custom-config-map"
                definition:
                apiVersion: v1
                kind: ConfigMap
                metadata:
                    name: "config-map"
                    namespace: "apps"
                data:
                    setting1: "value1"
                    setting2: "value2"



        """
        super().__init__(scope, config.get("name", "eks-cluster"), **kwargs)
        self.name = config.get("name", "eks-cluster")

        
        cluster_role = self.create_cluster_role()
        node_role = self.create_node_role()

        
        self.cluster = eks.Cluster(
            self,
            self.name,
            cluster_name=self.name,
            vpc=vpc,
            vpc_subnets=[{"subnet_type": ec2.SubnetType.PRIVATE_WITH_EGRESS}],
            default_capacity=config.get("default_capacity", 2),
            default_capacity_instance=ec2.InstanceType(config.get("default_instance_type", "t3.medium")),
            role=cluster_role,
            version=eks.KubernetesVersion.V1_28,
            kubectl_layer=KubectlV28Layer(self, "kubectl"),
            output_cluster_name=True,
            output_config_command=True,
            endpoint_access=config.get("endpoint_access", eks.EndpointAccess.PUBLIC_AND_PRIVATE),
        )

        
        self.add_admin_roles(config.get("admin_roles", []))

        
        self.add_node_groups(config.get("node_groups", []), node_role)

        
        self.add_fargate_profiles(config.get("fargate_profiles", []))

       
        self.add_helm_charts(config.get("helm_charts", []))

        
        self.add_manifests(config.get("manifests", []))

    def create_cluster_role(self):
        """Creates the IAM Role for the EKS cluster."""
        return iam.Role(
            self,
            f"{self.name}-cluster-role",
            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy"),
            ],
        )

    def create_node_role(self):
        """Creates the IAM Role for worker nodes."""
        return iam.Role(
            self,
            f"{self.name}-node-role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSWorkerNodePolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKS_CNI_Policy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"),
            ],
        )

    def add_admin_roles(self, admin_roles):
        """Maps specified admin IAM roles to Kubernetes `system:masters` group."""
        for admin_role_dict  in admin_roles:
            admin_arn = admin_role_dict['arn']
            admin_role = iam.Role.from_role_arn(
                self,
                f"AdminRole-{admin_arn.split('/')[-1]}",
                admin_arn,
            )
            self.cluster.aws_auth.add_masters_role(admin_role)

    def add_node_groups(self, node_groups, node_role):
        """Adds node groups to the cluster."""
        for ng_config in node_groups:
            node_group = self.cluster.add_nodegroup_capacity(
                f"{ng_config.get('name', 'default')}-ng",
                instance_types=[ec2.InstanceType(ng_config.get("instance_type", "t3.medium"))],
                min_size=ng_config.get("min_size", 1),
                max_size=ng_config.get("max_size", 3),
                desired_size=ng_config.get("desired_size", 2),
                node_role=node_role,
            )
            self.cluster.aws_auth.add_role_mapping(
                node_role,
                username="system:node:{{EC2PrivateDNSName}}",
                groups=[],
            )

    def add_fargate_profiles(self, fargate_profiles):
        """Adds Fargate profiles to the cluster."""
        for profile_config in fargate_profiles:
            self.cluster.add_fargate_profile(
                f"{profile_config.get('name', 'default')}-fp",
                selectors=[{"namespace": profile_config.get("namespace", "default")}],
            )

    def add_helm_charts(self, helm_charts):
        """Installs Helm charts in the cluster."""
        for chart_config in helm_charts:
            self.cluster.add_helm_chart(
                chart_config.get("name"),
                chart=chart_config.get("chart"),
                repository=chart_config.get("repository"),
                namespace=chart_config.get("namespace", "default"),
                values=chart_config.get("values", {}),
            )

    def add_manifests(self, manifests):
        """Adds Kubernetes manifests to the cluster."""
        for manifest in manifests:
            self.cluster.add_manifest(manifest.get("name"), manifest.get("definition"))