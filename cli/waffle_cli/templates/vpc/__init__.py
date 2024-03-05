from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]

from .parameters import Parameters
from .vpc import Vpc
from .flow_log import FlowLog
from .public_subnets import PublicSubnets
from .private_subnets import PrivateSubnets
from .security_groups import SecurityGroups
from .vpc_endpoints import VpcEndpoints
from .outputs import Outputs


def generate_vpc_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    vpc = Vpc(t, params)
    FlowLog(t, params, vpc)
    pb = PublicSubnets(t, params, vpc)
    pr = PrivateSubnets(t, params, vpc, pb)
    sg = SecurityGroups(t, params, vpc)
    VpcEndpoints(t, sg, vpc, pr)
    Outputs(t, vpc, sg, params, pr)

    return t.to_json()
