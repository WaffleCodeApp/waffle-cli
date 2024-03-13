from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Export,
    Join,
    Output,
    Ref,
    secretsmanager,
    Template,
)
from .parameters import Parameters


class GithubSecret:
    secret: secretsmanager.Secret

    def __init__(self, t: Template, p: Parameters):
        self.secret = t.add_resource(
            secretsmanager.Secret(
                "GithubSecret",
                Description=Join(
                    "",
                    [Ref(p.deployment_id), "-github"],
                ),
                SecretString='{"token":""}',
            )
        )

        t.add_output(
            [
                Output(
                    "GithubSecretArn",
                    Description="The arn of the github_secret",
                    Value=Ref(self.secret),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-GithubSecretArn"])
                    ),
                ),
            ]
        )
