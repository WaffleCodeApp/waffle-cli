from enum import Enum


class AuthType(str, Enum):
    USERPOOL = "USERPOOL"
    # OIDC = "OIDC"
    CUSTOM = "CUSTOM"
