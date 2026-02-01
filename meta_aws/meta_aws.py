from abc import ABC, abstractmethod
from typing import Any


class MetaAWS(ABC):

    def __init__(self, arn: str, boto_func: Any):
        self.arn = arn
        self.boto_func = boto_func
        self.role_name = self.set_role_from_arn(arn=arn)

    @staticmethod
    def set_role_from_arn(arn: str) -> str:
        """
            Parse ARN and extract role name if any
        """
        if MetaAWS._is_role_arn(arn=arn):
            splitted_arn = arn.split(":")
            service = splitted_arn[2]
            # IAM role
            if service == "iam" and splitted_arn[5].startswith("role/"):
                return splitted_arn[5].split("/", 1)[1]
            # STS assumed role
            if service == "sts" and splitted_arn[5].startswith("assumed-role/"):
                # assumed-role/RoleName/SessionName
                return splitted_arn[5].split("/", 2)[1]
        return ""

    @staticmethod
    def _is_role_arn(arn: str) -> bool:
        lower_end_arn = arn.lower().split(":")[5].split("/")[0]
        if any(x == lower_end_arn for x in ["assumed-role", "role"]):
            return True
        return False
