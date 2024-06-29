from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Equals,
    Ref,
    Template,
)
from .parameters import Parameters


class Conditions:
    allow_admin_create_user_only: str = "ALLOW_ADMIN_CREATE_USER_ONLY"

    def __init__(self, t: Template, p: Parameters) -> None:
        t.add_condition(
            self.allow_admin_create_user_only,
            Equals(Ref(p.allow_admin_create_user_only), "True"),
        )
