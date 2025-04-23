from collections import defaultdict

class ResourceRegistry:
    def __init__(self):
        self._resources = defaultdict(dict)

    def register(self, type_name: str, name: str, instance: object):
        # Debug logging
        print(f"Registering resource - Type: {type_name}, Name: {name}, Instance: {instance}")
        self._resources[type_name][name] = instance
        print(f"Successfully registered {name} of type {type_name}")
    def get(self, type_name: str, name: str, attribute: str = None):
        if name is None:
            raise ValueError(f"Missing name for resource type '{type_name}'")
        obj = self._resources[type_name].get(name)
        if not obj:
            raise KeyError(f"{type_name} named '{name}' not found.")
        return getattr(obj, attribute) if attribute else obj

    def maybe_get(self, type_name: str, name: str, attribute: str = None):
        if not name:
            return None
        obj = self._resources[type_name].get(name)
        return getattr(obj, attribute) if (obj and attribute) else obj

    def all(self):
        return self._resources