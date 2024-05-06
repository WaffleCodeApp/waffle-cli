from pydantic import BaseModel


class ApiStackSetting(BaseModel):
    subdomain: str = "api"
    custom_certificate_arn: str | None = None
