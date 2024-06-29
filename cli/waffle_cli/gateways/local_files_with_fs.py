from ..application_logic.gateway_interfaces.local_files import LocalFiles


SETTINGS_DIR = "./.waffle"


class LocalFilesWithFs(LocalFiles):
    def store_file(self, file_name: str, content: str) -> None:
        with open(
            f"{SETTINGS_DIR}/{file_name}",
            "w",
            encoding="UTF-8",
        ) as f:
            f.write(content)
