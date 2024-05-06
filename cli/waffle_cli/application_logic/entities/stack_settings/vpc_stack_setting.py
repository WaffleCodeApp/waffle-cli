from pydantic import BaseModel


class VpcStackSetting(BaseModel):
    vpc_cidr: str
    primary_private_cidr: str
    secondary_private_cidr: str
    primary_public_cidr: str
    secondary_public_cidr: str
