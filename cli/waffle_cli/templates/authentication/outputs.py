from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Export,
    GetAtt,
    If,
    Join,
    Output,
    Ref,
    Template,
)

from .user_pool import UserPool
from .idenity_pool import IdentityPool
from .parameters import Parameters
from .conditions import Conditions


class Outputs:
    def __init__(
        self, t: Template, up: UserPool, ip: IdentityPool, p: Parameters, c: Conditions
    ):
        t.add_output(
            [
                Output(
                    "AuthCreateUserPool",
                    Description="AuthCreateUserPool",
                    Value=If(
                        c.create_userpool_selected,
                        "True",
                        "False",
                    ),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-AuthCreateUserPool"])
                    ),
                ),
                Output(
                    "AuthUserPoolRef",
                    Description="AuthUserPoolRef",
                    Value=If(
                        c.create_userpool_selected,
                        Ref(up.user_pool),
                        "*",
                    ),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-AuthUserPoolRef"])
                    ),
                ),
                Output(
                    "AuthUserPoolArn",
                    Description="AuthUserPoolArn",
                    Value=If(
                        c.create_userpool_selected,
                        GetAtt(up.user_pool, "Arn"),
                        "*",
                    ),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-AuthUserPoolArn"])
                    ),
                ),
                Output(
                    "AuthUserPoolClientWebRef",
                    Description="AuthUserPoolClientWebRef",
                    Value=If(
                        c.create_userpool_selected,
                        Ref(up.web_client),
                        "*",
                    ),
                    Export=Export(
                        name=Join(
                            "", [Ref(p.deployment_id), "-AuthUserPoolClientWebRef"]
                        )
                    ),
                ),
                Output(
                    "AuthIdentityPoolRef",
                    Description="AuthIdentityPoolRef",
                    Value=Ref(ip.identity_pool),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-AuthIdentityPoolRef"])
                    ),
                ),
                Output(
                    "AuthRoleName",
                    Description="The name of the authorized role for admin",
                    Value=Ref(ip.auth_role),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-AuthRoleName"])
                    ),
                ),
                Output(
                    "AuthRoleArn",
                    Description="The ARN of the authorized role for users",
                    Value=GetAtt(ip.auth_role, "Arn"),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-AuthRoleArn"])
                    ),
                ),
                Output(
                    "AuthRoleId",
                    Description="The ID of the authorized role for users",
                    Value=GetAtt(ip.auth_role, "RoleId"),
                    Export=Export(name=Join("", [Ref(p.deployment_id), "-AuthRoleId"])),
                ),
            ]
        )
