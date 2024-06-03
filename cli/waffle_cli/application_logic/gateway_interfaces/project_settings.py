from typing import Protocol
from ..entities.project_setting import ProjectSetting


class ProjectSettings(Protocol):
    def create_or_update(self, project_setting: ProjectSetting) -> None: ...

    def get(self) -> ProjectSetting | None: ...
