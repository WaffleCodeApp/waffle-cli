import os
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.gateway_interfaces.deployment_settings import (
    DeploymentSettings,
)

SETTINGS_DIR = "./.waffle"


class DeploymentSettingsWithJson(DeploymentSettings):
    def create_or_update(self, deployment_setting: DeploymentSetting) -> None:
        deployment_id = deployment_setting.deployment_id
        with open(
            f"{SETTINGS_DIR}/{deployment_id}.json",
            "w",
            encoding="UTF-8",
        ) as settings_file:
            settings_file.write(deployment_setting.model_dump_json(indent=2))

    def get(self, deployment_id: str) -> DeploymentSetting | None:
        try:
            with open(
                f"{SETTINGS_DIR}/{deployment_id}.json", "r", encoding="UTF-8"
            ) as settings_file:
                settings_data: str = settings_file.read()
                return DeploymentSetting.model_validate_json(settings_data)
        except FileNotFoundError:
            return None

    def get_names(self) -> list[str]:
        return [f[:-5] for f in os.listdir(SETTINGS_DIR) if f.endswith(".json")]
