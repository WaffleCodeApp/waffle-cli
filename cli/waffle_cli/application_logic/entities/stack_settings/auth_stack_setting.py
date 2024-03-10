from enum import Enum
from .stack_setting import StackSetting


class AuthType(str, Enum):
    USERPOOL = "USERPOOL"
    OIDC = "OIDC"


class AuthStackSetting(StackSetting):
    auth_type: AuthType = AuthType.OIDC
