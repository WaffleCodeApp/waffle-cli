from enum import Enum

from pydantic import BaseModel


class AuthType(str, Enum):
    USERPOOL = "USERPOOL"
    OIDC = "OIDC"


class AuthStackSetting(BaseModel):
    auth_type: AuthType = AuthType.OIDC
