from ..application_logic.entities.deployment_state import DeploymentState
from ..application_logic.gateway_interfaces.deployment_states import DeploymentStates

SETTINGS_DIR = "./.waffle/deployment_states"


class DeploymentStatesWithJson(DeploymentStates):
    def create_or_update(self, deployment_state: DeploymentState) -> None:
        deployment_id = deployment_state.deployment_id
        with open(
            f"{SETTINGS_DIR}/{deployment_id}.json",
            "w",
            encoding="UTF-8",
        ) as states_file:
            states_file.write(deployment_state.model_dump_json(indent=2))

    def get(self, deployment_id: str) -> DeploymentState | None:
        try:
            with open(
                f"{SETTINGS_DIR}/{deployment_id}.json", "r", encoding="UTF-8"
            ) as states_file:
                states_data: str = states_file.read()
                return DeploymentState.model_validate_json(states_data)
        except FileNotFoundError:
            return None
