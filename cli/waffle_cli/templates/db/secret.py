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
                "DbMasterSecret",
                Description=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.database_id),
                        "PostgreSQL Master User Secret",
                    ],
                ),
                GenerateSecretString=secretsmanager.GenerateSecretString(
                    SecretStringTemplate='{"username": "master"}',
                    GenerateStringKey="password",
                    ExcludeCharacters='"@/\\',
                    PasswordLength=16,
                ),
            )
        )
