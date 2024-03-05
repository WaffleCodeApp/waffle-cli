from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Equals,
    Ref,
    Template,
)
from .parameters import Parameters


class Conditions:
    is_prod: str = "IS_PROD"
    create_userpool_selected: str = "CREATE_USERPOOL_SELECTED"

    def __init__(self, t: Template, p: Parameters) -> None:
        t.add_condition(
            self.create_userpool_selected, Equals(Ref(p.create_userpool), "True")
        )
