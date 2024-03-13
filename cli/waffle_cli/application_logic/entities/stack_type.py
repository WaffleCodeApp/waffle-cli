from enum import Enum


class StackType(str, Enum):
    vpc = "vpc"
    auth = "auth"
    api = "api"
    alerts = "alerts"
    github = "github"
    deployment = "deployment"
    db = "db"
    cdn_cicd = "cdn_cicd"
    cfn_cicd = "cfn_cicd"
    ecs_cicd = "ecs_cicd"
