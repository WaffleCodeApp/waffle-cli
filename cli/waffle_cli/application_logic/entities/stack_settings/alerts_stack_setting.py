from pydantic import BaseModel


class AlertsStackSetting(BaseModel):
    email_notifications: str
