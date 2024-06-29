from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]

from .parameters import Parameters
from .conditions import Conditions
from .roles import Roles
from .user_pool import UserPool
from .idenity_pool import IdentityPool
from .outputs import Outputs


def generate_auth_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    c = Conditions(t, params)
    roles = Roles(t, params)
    up = UserPool(t, params, roles, c)
    ip = IdentityPool(t, params, up)
    Outputs(t, up, ip, params)
    return t.to_json()


def generate_auth_parameter_list(
    deployment_id: str, allow_admin_create_user_only: bool
) -> list[dict[str, str]]:
    return [
        {
            "ParameterKey": "DeploymentId",
            "ParameterValue": deployment_id,
        },
        {
            "ParameterKey": "AllowAdminCreateUserOnly",
            "ParameterValue": "True" if allow_admin_create_user_only else "False",
        },
    ]
