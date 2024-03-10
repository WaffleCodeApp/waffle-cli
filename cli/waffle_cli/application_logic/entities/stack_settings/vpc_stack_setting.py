from .stack_setting import StackSetting


class VpcStackSetting(StackSetting):
    vpc_cidr: str
    primary_private_cidr: str
    secondary_private_cidr: str
    primary_public_cidr: str
    secondary_public_cidr: str
