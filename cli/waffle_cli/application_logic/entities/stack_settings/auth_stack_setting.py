from enum import Enum
from .stack_setting import StackSetting


class AuthtType(str, Enum):
    USERPOOL = "USERPOOL"
    OIDC = "OIDC"


class AuthStackSetting(StackSetting):
    auth_type: AuthtType = AuthtType.OIDC
