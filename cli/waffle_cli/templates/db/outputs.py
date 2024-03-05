from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Export,
    Join,
    Output,
    Ref,
    Template,
    ssm,
)
from .secret import Secret
from .parameters import Parameters


class Outputs:
    def __init__(
        self,
        t: Template,
        p: Parameters,
        s: Secret,
    ):
        t.add_output(
            [
                Output(
                    "DbSecretArn",
                    Description="The name of the secret with the credentials of the db",
                    Value=Ref(s.secret),
                    Export=Export(
                        name=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.database_id),
                                "-DbSecretArn",
                            ],
                        )
                    ),
                ),
            ]
        )

        t.add_resource(
            ssm.Parameter(
                "DBCredentialsParameter",
                Name=Join(
                    "",
                    [
                        "/",
                        Ref(p.deployment_id),
                        "/db/",
                        Ref(p.database_id),
                        "/secretName",
                    ],
                ),
                Type="String",
                Value=Ref(s.secret),
                Description="The name of the secret with the credentials of the db",
            )
        )
