class MissingKeyException(Exception):
    """
    Custom exception for missing mandatory keys in configuration services.
    """

    def __init__(self, service_name, missing_keys):
        message = (
            f"Service '{service_name}' is missing mandatory keys: {missing_keys}\n"
        )
        super().__init__(message)
        self.service_name = service_name
        self.missing_keys = missing_keys
