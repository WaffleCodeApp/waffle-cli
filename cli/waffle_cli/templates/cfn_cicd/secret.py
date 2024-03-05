from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Join,
    Ref,
    secretsmanager,
    Template,
)
from .parameters import Parameters


class Secret:
    secret: secretsmanager.Secret

    def __init__(self, t: Template, p: Parameters):
        self.secret = t.add_resource(
            secretsmanager.Secret(
                "Secret",
                Description=Join(
                    "",
                    [Ref(p.deployment_id), Ref(p.pipeline_id)],
                ),
                SecretString="{}",
            )
        )
