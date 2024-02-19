from argparse import ArgumentParser
from typing import Any, Protocol


class Command(Protocol):
    name: str
    description: str

    @classmethod
    def get_name(cls) -> str:
        return cls.name

    @classmethod
    def get_descrtiption(cls) -> str:
        return cls.description

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None: ...

    @staticmethod
    def execute(**_: Any) -> None: ...
