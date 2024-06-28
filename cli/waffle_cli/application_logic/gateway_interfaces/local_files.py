from typing import Protocol


class LocalFiles(Protocol):
    def store_file(self, file_name: str, content: str) -> None: ...
