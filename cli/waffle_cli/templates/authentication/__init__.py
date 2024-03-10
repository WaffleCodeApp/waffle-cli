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
    conditions = Conditions(t, params)
    roles = Roles(t, params)
    up = UserPool(t, params, conditions, roles)
    ip = IdentityPool(t, params, up)
    Outputs(t, up, ip, params, conditions)
    return t.to_json()


def generate_auth_parameter_list(
    deployment_id: str,
    create_userpool: str,
    invitation_sms_text: str | None = None,
    authentication_sms_text: str | None = None,
    verification_sms_text: str | None = None,
) -> list[dict[str, str]]:
    return [
        {
            "ParameterKey": "DeploymentId",
            "ParameterValue": deployment_id,
        },
        {
            "ParameterKey": "CreateUserpool",
            "ParameterValue": create_userpool,
        },
        {
            "ParameterKey": "AuthUserInvitationSMSText",
            "ParameterValue": invitation_sms_text or "",
        },
        {
            "ParameterKey": "AuthUserAuthenticationSMSText",
            "ParameterValue": authentication_sms_text or "",
        },
        {
            "ParameterKey": "AuthUserVerificationSMSText",
            "ParameterValue": verification_sms_text or "",
        },
    ]
