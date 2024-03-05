from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Join,
    logs,
    Ref,
    Template,
)

from .parameters import Parameters


class LoggingGroup:
    group: logs.LogGroup

    def __init__(self, t: Template, p: Parameters):
        self.group = t.add_resource(
            logs.LogGroup(
                "LogGroup",
                LogGroupName=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.pipeline_id),
                    ],
                ),
                RetentionInDays=365,
                UpdateReplacePolicy="Retain",
            )
        )
