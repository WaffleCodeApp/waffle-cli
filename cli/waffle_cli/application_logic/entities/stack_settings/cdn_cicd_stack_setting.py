from .cicd_stack_setting import CicdStackSetting


class CdnCicdStackSetting(CicdStackSetting):
    alias_hostname: str | None = None
    alias_cert_arn: str | None = None
