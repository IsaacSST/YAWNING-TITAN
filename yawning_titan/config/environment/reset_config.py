from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from yawning_titan.config.game_config.config_abc import ConfigABC
from yawning_titan.envs.generic.helpers.environment_input_validation import check_type


@dataclass()
class ResetConfig(ConfigABC):
    """Class that validates and stores the Reset Configuration."""

    _randomise_vulnerabilities_on_reset: bool
    _choose_new_high_value_nodes_on_reset: bool
    _choose_new_entry_nodes_on_reset: bool

    # region Getters
    @property
    def randomise_vulnerabilities_on_reset(self) -> bool:
        """Randomise vulnerabilities on reset."""
        return self._randomise_vulnerabilities_on_reset

    @property
    def choose_new_high_value_nodes_on_reset(self) -> bool:
        """Choose new high value nodes on reset."""
        return self._choose_new_high_value_nodes_on_reset

    @property
    def choose_new_entry_nodes_on_reset(self) -> bool:
        """Choose new entry nodes on reset."""
        return self._choose_new_entry_nodes_on_reset

    # endregion

    # region Setters
    @randomise_vulnerabilities_on_reset.setter
    def randomise_vulnerabilities_on_reset(self, value):
        self._randomise_vulnerabilities_on_reset = value

    @choose_new_high_value_nodes_on_reset.setter
    def choose_new_high_value_nodes_on_reset(self, value):
        self._choose_new_high_value_nodes_on_reset = value

    @choose_new_entry_nodes_on_reset.setter
    def choose_new_entry_nodes_on_reset(self, value):
        self._choose_new_entry_nodes_on_reset = value

    # endregion
    @classmethod
    def create(cls, config_dict: Dict[str, Any]) -> ResetConfig:
        """
        Creates an instance of :class:`ResetConfig <yawning_titan.config.environment.reset_config.ResetConfig>.

        This calls :func:`validate() <yawning_titan.config.environment.reset_config.ResetConfig.validate>.

        :param: config_dict: A config dict with the required key/values pairs.

        :return: An instance of :class:`ResetConfig <yawning_titan.config.environment.reset_config.ResetConfig>.
        """
        cls._validate(config_dict)

        reset_config = ResetConfig(
            _randomise_vulnerabilities_on_reset=config_dict[
                "randomise_vulnerabilities_on_reset"
            ],
            _choose_new_high_value_nodes_on_reset=config_dict[
                "choose_new_high_value_nodes_on_reset"
            ],
            _choose_new_entry_nodes_on_reset=config_dict[
                "choose_new_entry_nodes_on_reset"
            ],
        )

        return reset_config

    @classmethod
    def _validate(cls, config_dict: dict):
        for name in [
            "randomise_vulnerabilities_on_reset",
            "choose_new_high_value_nodes_on_reset",
            "choose_new_entry_nodes_on_reset",
        ]:
            check_type(config_dict, name, [bool])
