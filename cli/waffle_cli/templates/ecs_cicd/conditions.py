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

    custom_vpc_ref: str = "CUSTOM_VPC_REF"
    custom_vpc_cidr_block: str = "CUSTOM_VPC_CIDR_BLOCK"
    custom_primary_private_subnet_ref: str = "CUSTOM_PRIMARY_PRIVATE_SUBNET_REF"
    custom_secondary_private_subnet_ref: str = "CUSTOM_SECONDARY_PRIVATE_SUBNET_REF"
    # custom_local_incoming_connections_sg: str = "CUSTOM_LOCAL_INCOMMING_CONNECTIONS_SG"
    custom_local_outgoing_connections_sg: str = "CUSTOM_LOCAL_OUTGOING_CONNECTIONS_SG"
    custom_nat_outgoing_connections_sg: str = "CUSTOM_NAT_OUTGOING_CONNECTIONS_SG"
    custom_ecr_incoming_connections_sg: str = "CUSTOM_ECR_INCOMMING_CONNECTIONS_SG"
    custom_github_secret_arn: str = "CUSTOM_GITHUB_TOKEN_SECRET_NAME"
    custom_user_pool_arn: str = "CUSTOM_USER_POOL_ARN"
    custom_restapi_id: str = "CUSTOM_RESAPI_ID"
    custom_root_resource_id: str = "CUSTOM_ROOT_RESOURCE_ID"
    custom_alerts_sns_ref: str = "CUSTOM_ALERT_SNS_REF"
    custom_deployment_secret_arn: str = "CUSTOM_DEPLOYMENT_SECRET_ARN"

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
            self.custom_vpc_ref,
            Not(Equals(Ref(p.vpc_ref), "")),
        )

        t.add_condition(
            self.custom_vpc_cidr_block,
            Not(Equals(Ref(p.vpc_cidr_block), "")),
        )

        t.add_condition(
            self.custom_primary_private_subnet_ref,
            Not(Equals(Ref(p.primary_private_subnet_ref), "")),
        )

        t.add_condition(
            self.custom_secondary_private_subnet_ref,
            Not(Equals(Ref(p.secondary_private_subnet_ref), "")),
        )

        # t.add_condition(
        #     self.custom_local_incoming_connections_sg,
        #     Not(Equals(Ref(p.local_incoming_connections_sg), "")),
        # )

        t.add_condition(
            self.custom_local_outgoing_connections_sg,
            Not(Equals(Ref(p.local_outgoing_connection_security_group_id), "")),
        )

        t.add_condition(
            self.custom_nat_outgoing_connections_sg,
            Not(Equals(Ref(p.nat_outgoing_connection_security_group_id), "")),
        )

        t.add_condition(
            self.custom_ecr_incoming_connections_sg,
            Not(Equals(Ref(p.ecr_incoming_connection_security_group_id), "")),
        )

        t.add_condition(
            self.custom_github_secret_arn,
            Not(Equals(Ref(p.github_secret_arn), "")),
        )

        t.add_condition(
            self.custom_user_pool_arn,
            Not(Equals(Ref(p.user_pool_arn), "")),
        )

        t.add_condition(
            self.custom_restapi_id,
            Not(Equals(Ref(p.restapi_id), "")),
        )

        t.add_condition(
            self.custom_root_resource_id,
            Not(Equals(Ref(p.root_resource_id), "")),
        )

        t.add_condition(
            self.custom_root_resource_id,
            Not(Equals(Ref(p.root_resource_id), "")),
        )

        t.add_condition(
            self.custom_alerts_sns_ref,
            Not(Equals(Ref(p.alerts_sns_ref), "")),
        )

        t.add_condition(
            self.custom_deployment_secret_arn,
            Not(Equals(Ref(p.deployment_secret_arn), "")),
        )
