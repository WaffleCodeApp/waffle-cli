from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]
from .parameters import Parameters
from .alerts_sns import AlertsSns


def generate_alerts_stack_json() -> str:
    t = Template()
    parameters = Parameters(t)
    AlertsSns(t, parameters)

    return t.to_json()
