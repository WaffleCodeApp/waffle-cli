from .stack_setting import StackSetting


class VpcStackSetting(StackSetting):
    vpc_cidr: str | None = None
    primary_private_cidr: str | None = None
    secondary_private_cidr: str | None = None
    primary_public_cidr: str | None = None
    secondary_public_cidr: str | None = None
