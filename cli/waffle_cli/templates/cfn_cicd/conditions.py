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

    custom_full_domain_name: str = "CUSTOM_FULL_DOMAIN_NAME"
    custom_backend_api_hostname: str = "CUSTOM_BACKEND_API_HOSTNAME"
    custom_vpc_ref: str = "CUSTOM_VPC_REF"
    custom_primary_private_subnet_ref: str = "CUSTOM_PRIMARY_PRIVATE_SUBNET_REF"
    custom_secondary_private_subnet_ref: str = "CUSTOM_SECONDARY_PRIVATE_SUBNET_REF"
    custom_local_outgoing_connections_sg: str = "CUSTOM_LOCAL_OUTGOING_CONNECTIONS_SG"
    custom_nat_outgoing_connections_sg: str = "CUSTOM_NAT_OUTGOING_CONNECTIONS_SG"
    custom_restapi_id: str = "CUSTOM_RESTAPI_ID"
    custom_root_resource_id: str = "CUSTOM_ROOT_RESOURCE_ID"
    custom_api_protocol: str = "CUSTOM_API_PROTOCOL"
    custom_api_host: str = "CUSTOM_API_HOST"
    custom_api_stage: str = "CUSTOM_API_STAGE"
    custom_user_pool_ref: str = "CUSTOM_USER_POOL_REF"
    custom_user_pool_arn: str = "CUSTOM_USER_POOL_ARN"
    custom_identity_pool_ref: str = "CUSTOM_IDENTITY_POOL_REF"
    custom_alerts_sns_ref: str = "CUSTOM_ALERT_SNS_REF"
    custom_deployment_secret_arn: str = "CUSTOM_DEPLOYMENT_SECRET_ARN"
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
            self.custom_full_domain_name,
            Not(Equals(Ref(p.full_domain_name), "")),
        )

        t.add_condition(
            self.custom_backend_api_hostname,
            Not(Equals(Ref(p.api_subdomain), "")),
        )

        t.add_condition(
            self.custom_vpc_ref,
            Not(Equals(Ref(p.vpc_ref), "")),
        )

        t.add_condition(
            self.custom_primary_private_subnet_ref,
            Not(Equals(Ref(p.primary_private_subnet_ref), "")),
        )

        t.add_condition(
            self.custom_secondary_private_subnet_ref,
            Not(Equals(Ref(p.secondary_private_subnet_ref), "")),
        )

        t.add_condition(
            self.custom_local_outgoing_connections_sg,
            Not(Equals(Ref(p.local_outgoing_connection_security_group_id), "")),
        )

        t.add_condition(
            self.custom_nat_outgoing_connections_sg,
            Not(Equals(Ref(p.nat_outgoing_connection_security_group_id), "")),
        )

        t.add_condition(
            self.custom_restapi_id,
            Not(Equals(Ref(p.restapi_id), "")),
        )

        t.add_condition(
            self.custom_root_resource_id,
            Not(Equals(Ref(p.root_resource_id), "")),
        )

        # t.add_condition(
        #     self.custom_stage_name,
        #     Not(Equals(Ref(p.stage_name), "")),
        # )

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
            self.custom_user_pool_arn,
            Not(Equals(Ref(p.user_pool_arn), "")),
        )

        t.add_condition(
            self.custom_identity_pool_ref,
            Not(Equals(Ref(p.identity_pool_ref), "")),
        )

        t.add_condition(
            self.custom_alerts_sns_ref,
            Not(Equals(Ref(p.alerts_sns_ref), "")),
        )

        t.add_condition(
            self.custom_deployment_secret_arn,
            Not(Equals(Ref(p.deployment_secret_arn), "")),
        )

        t.add_condition(
            self.custom_github_secret_arn,
            Not(Equals(Ref(p.github_secret_arn), "")),
        )
