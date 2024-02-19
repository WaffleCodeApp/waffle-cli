from .stack_setting import StackSetting


class ApiStackSetting(StackSetting):
    subdomain: str | None = "api"
