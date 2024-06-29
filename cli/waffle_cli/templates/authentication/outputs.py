from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Export,
    GetAtt,
    Join,
    Output,
    Ref,
    Template,
)

from .user_pool import UserPool
from .idenity_pool import IdentityPool
from .parameters import Parameters


class Outputs:
    def __init__(self, t: Template, up: UserPool, ip: IdentityPool, p: Parameters):
        t.add_output(
            [
                Output(
                    "AuthUserPoolRef",
                    Description="AuthUserPoolRef",
                    Value=Ref(up.user_pool),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-AuthUserPoolRef"])
                    ),
                ),
                Output(
                    "AuthUserPoolArn",
                    Description="AuthUserPoolArn",
                    Value=GetAtt(up.user_pool, "Arn"),
                    Export=Export(
                        name=Join("", [Ref(p.deployment_id), "-AuthUserPoolArn"])
                    ),
                ),
                Output(
                    "AuthUserPoolClientWebRef",
                    Description="AuthUserPoolClientWebRef",
                    Value=Ref(up.web_client),
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
