from .stack_setting import StackSetting


class ApiStackSetting(StackSetting):
    subdomain: str = "api"
    custom_certificate_arn: str | None = None
