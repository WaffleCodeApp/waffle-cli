from argparse import ArgumentParser
import re
from typing import Any

from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import BLUE, GREEN, NEUTRAL, RED, YELLOW
from .command_type import Command
from .create_deployment_settings import CreateDeploymentSettings
from .configure_aws_profile import ConfigureAwsProfile
from .configure_deployment_domain import ConfigureDeploymentDomain
from .create_deployment_certificate import CreateDeploymentCertificate
from .deploy_vpc import DeployVpc
from .deploy_api import DeployApi
from .deploy_auth_userpool import DeployAuthUserPool
from .deploy_alerts import DeployAlerts
from .deploy_github import DeployGithub
from .set_deployment_defaults import SetDeploymentDefaults


class CreateDeploymentWizard(Command):
    name = "create_deployment_wizard"
    description = "Step-by-step create a deployment."

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        pass

    @staticmethod
    def execute(gateways: Gateways = gateway_implementations, **__: Any) -> None:
        print(
            NEUTRAL
            + "Waffle is a toolkit to help deploy complete web-applications to secure "
            + "environments in AWS.\n\n"
            + "This tool helps set up a deployment step-by-step interactively.\n\n"
            + YELLOW
            + "If you want to use custom templates or existing resources, then "
            + "you need to do a custom installation, prease refer to the docs.\n\n"
            + NEUTRAL
        )
        while True:
            proceed = input("Do you want to proceed? [Y]/n ")
            if proceed.lower() == "y" or proceed == "":
                break
            elif proceed.lower() == "n":
                return

        # -------------
        # deployment_id
        # -------------

        print(
            "\n\n"
            + BLUE
            + f"Choose your deployment id.\n\n"
            + NEUTRAL
            + "A deployment is a fully-featured complete set of hosted instances of the "
            + "services of your application. Deployments are independent, sharing no resources.\n\n"
            + "The deployment id can be any string of your choice. It refers to "
            + "your deployment. It's a common practice to have deployments for each "
            + "major step in your software development life cycle. In this case the "
            + "deployment_id can be the name of the development phase the deployment is "
            + "used for, like development | production | qa | testing | staging.\n\n"
        )
        deployment_id: str = ""
        while True:
            deployment_id = input("deployment_id: (only letters and numbers) ")
            if re.match("^[a-z,0-9]+$", deployment_id):
                break
            print(RED + "Only letters and numbers are supported." + NEUTRAL)

        CreateDeploymentSettings.execute(deployment_id=deployment_id)

        print("\n\n" + BLUE + f"Choose the AWS region to deploy to.\n\n" + NEUTRAL)

        aws_region: str = ""
        while True:
            aws_region = input("aws region: (like us-east-1 for example) ")
            if aws_region in [
                "ap-south-1",
                "eu-north-1",
                "eu-west-3",
                "eu-west-2",
                "eu-west-1",
                "ap-northeast-3",
                "ap-northeast-2",
                "ap-northeast-1",
                "ca-central-1",
                "sa-east-1",
                "ap-southeast-1",
                "ap-southeast-2",
                "eu-central-1",
                "us-east-1",
                "us-east-2",
                "us-west-1",
                "us-west-2",
            ]:
                break
            print(RED + "Unrecognized region name." + NEUTRAL)

        # -------------------
        # deployment defaults
        # -------------------

        print(
            "\n\n"
            + NEUTRAL
            + "Deployments typically have slightly different requirements in the different "
            + "SLDC phases. While a production environment is typically required to have "
            + "the logs and backups retained, and alarms set up to indicate risks, a development "
            + "environment might require cost saving instead. "
            + "Next let's set up default settings for the stacks that are added later.\n\n"
            + BLUE
            + f"Default stack settings\n\n"
            + NEUTRAL
        )

        default_log_retention_days: str = ""
        while True:
            default_log_retention_days = input(
                "Default log retention (days): [0, 7 or 365] "
            )
            if default_log_retention_days in ["0", "7", "365"]:
                break
            print(RED + "Please choose from 0, 7 or 365." + NEUTRAL)

        default_alarms_enabled: str = ""
        while True:
            default_alarms_enabled = input("Alarms enabled by default: [yes or no] ")
            if default_alarms_enabled.lower() in [
                "y",
                "yes",
                "n",
                "no",
                "true",
                "false",
            ]:
                break
            print(RED + "Please respond with yes or no." + NEUTRAL)

        default_db_backup_retention: str = ""
        while True:
            default_db_backup_retention = input(
                "Default database backup retention (days): [0, 7 or 35] "
            )
            if default_db_backup_retention in ["0", "7", "35"]:
                break
            print(RED + "Please choose from 0, 7 or 35." + NEUTRAL)

        default_require_manual_cicd_approval: str = ""
        while True:
            default_require_manual_cicd_approval = input(
                "CICD pipelines require manual approval before deployment by default: [yes or no] "
            )
            if default_require_manual_cicd_approval.lower() in [
                "y",
                "yes",
                "n",
                "no",
                "true",
                "false",
            ]:
                break
            print(RED + "Please respond with yes or no." + NEUTRAL)

        SetDeploymentDefaults.execute(
            deployment_id=deployment_id,
            default_log_retention_days=int(default_log_retention_days),
            default_alarms_enabled=(
                "True" if default_alarms_enabled in ["y", "yes", "true"] else "False"
            ),
            default_db_backup_retention=int(default_db_backup_retention),
            default_require_manual_cicd_approval=(
                "True"
                if default_require_manual_cicd_approval in ["y", "yes", "true"]
                else "False"
            ),
        )

        # -----------
        # aws profile
        # -----------

        print(
            "\n\n"
            + NEUTRAL
            + "Each deployment has to have access to AWS. The way this tool works if that "
            + "it expects that there is an local AWS profile on the computer running the cli, "
            + "for every deployment. The AWS profile ids are the same as the deployment ids. "
            + "For example if you trigger a CLI command for your 'development' deployment_id, "
            + "then it will try to use the local AWS profile with the name 'development' too.\n\n"
            + "The next step registers a local AWS profile with your chosen deployment_id.\n\n"
            + BLUE
            + f"Setting up a local AWS profile for {deployment_id}.\n\n"
            + NEUTRAL
        )

        ConfigureAwsProfile.execute(deployment_id=deployment_id)

        # ----------------
        # full_domain_name
        # ----------------

        print(
            "\n\n"
            + NEUTRAL
            + "Each deployment has to have a root domain name. Services that have public hostnames "
            + "will be set up to use a subdomain of the deployment's root domain. You have to own "
            + "the parent domain name of the deployment's root domain name. the Some of the stacks "
            + "enable to define additinal alternative domains too.\n\n"
            + "For examaple:\n"
            + "- Let's say you own: example.com\n"
            + "- You can set the deployment root domain to be: development.example.com\n"
            + "- HTTP REST endpoints will be automacitally pointed to: api.development.example.com\n"
            + "- The frontend will be: frontend.development.example.com\n"
            + "- Custom alternative frontend can be: www.anythingelse.com at a later point.\n\n"
            + "This tools sets a DNS configuration up in the deployment's AWS account. "
            + "In order for it to work, you'll have to add the NS records that are created "
            + "to your existing DNS settings manually.\n\n"
            + "For example if you own example.com and now you're creating development.example.com "
            + "then the tool creates NS records for development.example.com, and you have to add them "
            + "manually to wherever your DNS configuration for example.com is.\n\n"
            + BLUE
            + f"Choose the root domain name for this deployment.\n"
            + NEUTRAL
            + "\tA typical choice is to use <deployment_id>.<your_main_domain> "
            + "like for example deployment.example.com.\n\n"
        )

        full_domain_name: str = ""
        while True:
            full_domain_name = input("root domain name: (without https://) ")
            if re.match(r"^[a-z,0-9,.,\-,_]+$", full_domain_name):
                break

        ConfigureDeploymentDomain.execute(
            deployment_id=deployment_id, full_domain_name=full_domain_name
        )

        # -------------------
        # generic certificate
        # -------------------

        print(
            "\n\n"
            + NEUTRAL
            + "For next a generic HTTPS certificate is created that can serve "
            + f"HTTPS requests from https://{full_domain_name} and https://*.{full_domain_name} \n"
            + "This certificate will automatically be assigend to the frontends you "
            + "deploy and to the HTTP api: https://api.{full_domain_name}\n\n"
        )

        CreateDeploymentCertificate.execute(
            deployment_id=deployment_id,
        )

        # -------------------------
        # deploying the foundations
        # -------------------------

        print(
            "\n\n"
            + GREEN
            + "Next: deploying the foundational stacks to AWS.\n\n"
            + NEUTRAL
        )

        # ----------
        # deploy vpc
        # ----------

        print(
            "\n\n"
            + BLUE
            + "Virtual Private Cloud\n"
            + NEUTRAL
            + "\tDeploying: a VPC with private and public subnets in multi availability-zone "
            + "configuration, also setting up an internet gateway, NAT gateway and default "
            + "security groups that will control internal and external network communication.\n\n"
        )

        DeployVpc.execute(
            deployment_id=deployment_id,
        )

        # -----------
        # deploy api
        # -----------

        print(
            "\n\n"
            + NEUTRAL
            + "An API Gateway is going to be deployed, that can be used to host HTTP endpoints to "
            + "any backend services that we add later.\n\n"
            + BLUE
            + "API\n"
            + NEUTRAL
            + "\tDeploying: a VPC with private and public subnets in multi availability-zone "
            + "configuration, also setting up an internet gateway, NAT gateway and default "
            + "security groups that will control internal and external network communication.\n\n"
        )

        DeployApi.execute(
            deployment_id=deployment_id,
        )

        # -----------
        # deploy auth
        # -----------

        print(
            "\n\n"
            + BLUE
            + "Authentication\n\n"
            + NEUTRAL
            + "\tDeploying: a Cognito Identity Pool that can be used for IAM based authorization "
            + "with the API Gateway, and a Cognito User Pool as well, to store and manage user ceredentials.\n\n"
        )

        DeployAuthUserPool.execute(
            deployment_id=deployment_id,
        )

        # -------------
        # deploy alerts
        # -------------

        print(
            "\n\n"
            + NEUTRAL
            + "The services that are going to be deployed can trigger different alarms "
            + "in case they run out of CPU or memory resources, on execution issues and "
            + "other warnings. We are creating an SNS topic that these alarm notifications "
            + "will be sent to. The notifications by default will be delivered by email. "
            + "Optionally you can implement your own service that delivers the notifications "
            + "that are sent to this SNS topic to the communication channel of your choice.\n\n"
            + BLUE
            + "Alerts\n"
            + NEUTRAL
            + "\tDeploying: an SNS Topic with email delivery enabled.\n\n"
        )

        email_list: str = ""
        while True:
            email_list = input(
                "Email addresses to deliver notifications to: [comma separated list] "
            )
            if re.match(r"^[a-z,0-9,.,\-,_,@,\,]+$", email_list):
                break
        DeployAlerts.execute(deployment_id=deployment_id, email_list=email_list)

        # ------
        # GitHub
        # ------

        print(
            "\n\n"
            + NEUTRAL
            + "Your backend and frontend services will be deployed by CICD pipelines provided "
            + "by Waffle. In order for these pipelines to be able to fetch your srouces on changes "
            + "from your repositories hosted on GitHub, you have to provide an API key "
            + "that has permissions to access the repositories that you plan to deploy. "
            + "Details on how to create personal API keys for GitHub can be found here:\n"
            + "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens \n\n"
            + BLUE
            + "GitHub\n"
            + NEUTRAL
            + "\tDeploying: a Secret Manager secret storing the GitHub API key.\n\n"
        )

        github_access_token: str = ""
        while True:
            github_access_token = input("GitHub access token: ")
            if github_access_token != "":
                break

        DeployGithub.execute(
            deployment_id=deployment_id, access_token=github_access_token
        )

        print(NEUTRAL + "\n\n")

        gateways.stacks.wait_for_stacks_to_create_or_update(
            deployment_id=deployment_id, aws_region=aws_region
        )

        print(
            "\n\n"
            + GREEN
            + "Next: Proceed with adding services to your project.\n\n"
            + NEUTRAL
        )
