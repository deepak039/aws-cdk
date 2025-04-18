import networkx as nx
from typing import Dict, List


class DependencyResolver:
    def __init__(self, config: Dict):
        self.config = config
        self.natural_dependencies = {
            'alb': ['vpcs', 'asg'],
            'api_gateways': ['vpcs', 'lambdas'],
            'asg': ['vpcs'],
            'dynamodb': [],
            'ec2': ['vpcs', 'security_groups'],
            'eks': ['vpcs'],
            'elasticache': ['vpcs', 'security_groups', 'subnet_groups'],
            'iam_permissions': [],
            'lambdas': ['vpcs', 'security_groups','rds'],
            'nat_gateways': ['vpcs', 'subnet_groups'],
            'rds': ['vpcs', 'security_groups', 'subnet_groups'],
            's3_buckets': [],
            'security_groups': ['vpcs'],
            'subnet_groups': ['vpcs'],
            'vpcs': [],
            'vpc_endpoints': ['vpcs']
        }

    def resolve_dependencies(self) -> List[str]:
        """
        Resolves dependencies and returns a list of service keys
        sorted by dependency order.
        """
        dependency_graph = nx.DiGraph()

        # Add nodes and edges for dependencies
        for service, dependencies in self.natural_dependencies.items():
            dependency_graph.add_node(service)
            for dependency in dependencies:
                dependency_graph.add_edge(dependency, service)

        # Perform topological sort to ensure dependencies are resolved
        try:
            sorted_services = list(nx.topological_sort(dependency_graph))
        except nx.NetworkXUnfeasible:
            raise ValueError("Circular dependency detected among services.")

        # Return the sorted list of service keys
        return sorted_services

    def sort_configuration(self, config: Dict, sorted_services: List[str]) -> Dict:
        """
        Sorts the original configuration dictionary based on dependency order.
        """
        sorted_config = {}
        for service in sorted_services:
            if service in config:
                sorted_config[service] = config[service]
        return sorted_config