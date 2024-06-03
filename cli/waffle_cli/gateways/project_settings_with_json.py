from ..application_logic.entities.project_setting import ProjectSetting
from ..application_logic.gateway_interfaces.project_settings import (
    ProjectSettings,
)

SETTINGS_DIR = "./.waffle"


class ProjectSettingsWithJson(ProjectSettings):
    def create_or_update(self, project_setting: ProjectSetting) -> None:
        with open(
            f"{SETTINGS_DIR}/project.json",
            "w",
            encoding="UTF-8",
        ) as settings_file:
            settings_file.write(project_setting.model_dump_json(indent=2))

    def get(self) -> ProjectSetting | None:
        try:
            with open(
                f"{SETTINGS_DIR}/project.json", "r", encoding="UTF-8"
            ) as settings_file:
                settings_data: str = settings_file.read()
                return ProjectSetting.model_validate_json(settings_data)
        except FileNotFoundError:
            return None
