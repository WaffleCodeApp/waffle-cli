from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]


class Parameters:
    deployment_id: Parameter
    email_notification_list: Parameter

    def __init__(self, t: Template):
        self.deployment_id = t.add_parameter(
            Parameter("DeploymentId", Description="deployment_id", Type="String")
        )

        self.email_notification_list = t.add_parameter(
            Parameter(
                "EmailNotificationList",
                Description="The Email notification list is used to configure a "
                "SNS topic for sending cloudwatch alarm and SQS "
                "Event notifications",
                Type="String",
            )
        )
