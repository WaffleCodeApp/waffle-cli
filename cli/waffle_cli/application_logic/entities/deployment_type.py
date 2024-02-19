from enum import Enum


class DeploymentType(str, Enum):
    DEV = "DEV"
    PROD = "PROD"
