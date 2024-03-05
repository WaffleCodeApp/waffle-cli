from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Export,
    Join,
    Output,
    Ref,
    sns,
    Template,
)
from .parameters import Parameters


class AlertsSns:
    def __init__(self, t: Template, p: Parameters):
        alerts_sns_topic: sns.Topic = t.add_resource(
            sns.Topic(
                "SnsTopic",
                Subscription=[
                    sns.Subscription(
                        Endpoint=Ref(p.email_notification_list),
                        Protocol="email",
                    )
                ],
            )
        )

        t.add_output(
            [
                Output(
                    "AlertsSnsTopicRef",
                    Description="The Ref of the alerts sns",
                    Value=Ref(alerts_sns_topic),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-AlertsSnsTopicRef"])
                    ),
                ),
            ]
        )
