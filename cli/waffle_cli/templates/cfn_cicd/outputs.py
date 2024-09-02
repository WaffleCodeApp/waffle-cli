from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Export,
    Join,
    Output,
    Ref,
    Template,
)
from .parameters import Parameters


class Outputs:
    def __init__(
        self,
        t: Template,
        p: Parameters,
    ):
        t.add_output(
            [
                Output(
                    "StackExists",
                    Value="True",
                    Export=Export(
                        name=Join(
                            "",
                            [
                                "Waffle-cfn-cicd-",
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.pipeline_id),
                            ],
                        )
                    ),
                ),
            ]
        )
