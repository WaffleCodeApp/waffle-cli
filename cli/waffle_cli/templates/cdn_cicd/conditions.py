from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Equals,
    ImportValue,
    Join,
    Not,
    Ref,
    Template,
)
from application_logic.entities.deployment_type import DeploymentType
from .parameters import Parameters


class Conditions:
    is_prod: str = "IS_PROD"
    manual_approval_selected: str = "MANUAL_APPROVAL_SELECTED"
    create_userpool_selected: str = "CREATE_USERPOOL_SELECTED"

    alt_full_domain_name_specified: str = "ALT_FULL_DOMAIN_NAME_SPECIFIED"
    alt_certificate_arn: str = "ALT_CERTIFICATE_ARN"

    custom_api_protocol: str = "CUSTOM_API_PROTOCOL"
    custom_api_host: str = "CUSTOM_API_HOST"
    custom_api_stage: str = "CUSTOM_API_STAGE"
    custom_user_pool_ref: str = "CUSTOM_USER_POOL_REF"
    custom_auth_web_client: str = "CUSTOM_AUTH_WEB_CLIENT"
    custom_identity_pool_ref: str = "CUSTOM_IDENTITY_POOL_REF"

    custom_github_secret_arn: str = "CUSTOM_GITHUB_TOKEN_SECRET_NAME"

    def __init__(self, t: Template, p: Parameters) -> None:
        t.add_condition(
            self.is_prod,
            Equals(Ref(p.deployment_type), DeploymentType.PROD.value),
        )

        t.add_condition(
            self.manual_approval_selected, Equals(Ref(p.manual_approval), "True")
        )

        t.add_condition(
            self.create_userpool_selected,
            Equals(
                ImportValue(
                    Join(
                        "",
                        [
                            Ref(p.deployment_id),
                            "-AuthCreateUserPool",
                        ],
                    )
                ),
                "True",
            ),
        )

        t.add_condition(
            self.alt_full_domain_name_specified,
            Not(Equals(Ref(p.alt_full_domain_name), "")),
        )

        t.add_condition(
            self.alt_certificate_arn,
            Not(Equals(Ref(p.alt_certificate_arn), "")),
        )

        t.add_condition(
            self.custom_api_protocol,
            Not(Equals(Ref(p.api_protocol), "")),
        )

        t.add_condition(
            self.custom_api_host,
            Not(Equals(Ref(p.api_host), "")),
        )

        t.add_condition(
            self.custom_api_stage,
            Not(Equals(Ref(p.api_stage), "")),
        )

        t.add_condition(
            self.custom_user_pool_ref,
            Not(Equals(Ref(p.user_pool_ref), "")),
        )

        t.add_condition(
            self.custom_auth_web_client,
            Not(Equals(Ref(p.auth_web_client), "")),
        )

        t.add_condition(
            self.custom_identity_pool_ref,
            Not(Equals(Ref(p.identity_pool_ref), "")),
        )

        t.add_condition(
            self.custom_github_secret_arn,
            Not(Equals(Ref(p.github_secret_arn), "")),
        )
