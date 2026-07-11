class ActiveInstanceException(Exception):
    """Raised when attempting to delete an instance that is RUNNING."""

    def __init__(self, instance_id: int):
        self.instance_id = instance_id
        super().__init__(
            f"Instance {instance_id} is RUNNING and cannot be deleted. Stop it first."
        )


class NotFoundException(Exception):
    def __init__(self, resource: str, resource_id: int):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} {resource_id} not found")


class ForbiddenException(Exception):
    def __init__(self, detail: str = "You do not have permission to access this resource"):
        self.detail = detail
        super().__init__(detail)
