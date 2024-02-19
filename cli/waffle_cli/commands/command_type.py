from argparse import ArgumentParser
from typing import Any, Protocol
from abc import abstractmethod


class Command(Protocol):
    @staticmethod
    @abstractmethod
    def get_name() -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_descrtiption() -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def arg_parser(parser: ArgumentParser) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def execute(**_: dict[str, Any]) -> None:
        raise NotImplementedError
