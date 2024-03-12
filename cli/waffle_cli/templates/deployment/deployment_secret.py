from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Export,
    Join,
    Output,
    Ref,
    secretsmanager,
    Template,
)
from .parameters import Parameters


class DeploymentSecret:
    secret: secretsmanager.Secret

    def __init__(self, t: Template, p: Parameters):
        self.secret = t.add_resource(
            secretsmanager.Secret(
                "Secret",
                Description=Join(
                    "",
                    [Ref(p.deployment_id), "-generic"],
                ),
                SecretString="{}",
            )
        )

        t.add_output(
            [
                Output(
                    "DeploymentSecretArn",
                    Description="The arn of the deployment_secret",
                    Value=Ref(self.secret),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-DeploymentSecretArn"])
                    ),
                ),
            ]
        )
