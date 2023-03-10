from __future__ import annotations

from typing import Optional

from yawning_titan.config.core import ConfigGroup
from yawning_titan.db.doc_metadata import DocMetadata, DocMetaDataObject
from yawning_titan.game_modes.components.blue_agent import Blue
from yawning_titan.game_modes.components.game_rules import GameRules
from yawning_titan.game_modes.components.miscellaneous import Miscellaneous
from yawning_titan.game_modes.components.observation_space import ObservationSpace
from yawning_titan.game_modes.components.red_agent import Red
from yawning_titan.game_modes.components.reset import Reset
from yawning_titan.game_modes.components.rewards import Rewards

# --- Tier 0 groups


class GameMode(ConfigGroup, DocMetaDataObject):
    """All options to configure and represent a complete game mode."""

    def __init__(
        self,
        doc: Optional[str] = None,
        red: Red = None,
        blue: Blue = None,
        game_rules: GameRules = None,
        observation_space: ObservationSpace = None,
        on_reset: Reset = None,
        rewards: Rewards = None,
        miscellaneous: Miscellaneous = None,
        _doc_metadata: Optional[DocMetadata] = None,
    ):
        self.red: Red = red if red else Red()
        self.blue: Blue = blue if blue else Blue()
        self.game_rules: GameRules = game_rules if game_rules else GameRules()
        self.observation_space: ObservationSpace = (
            observation_space if observation_space else ObservationSpace()
        )
        self.on_reset: Reset = on_reset if on_reset else Reset()
        self.rewards: Rewards = rewards if rewards else Rewards()
        self.miscellaneous: Miscellaneous = (
            miscellaneous if miscellaneous else Miscellaneous()
        )
        self._doc_metadata = _doc_metadata if _doc_metadata else DocMetadata()
        super().__init__(doc)

    @classmethod
    def create_from_yaml(
        cls,
        yaml: Optional[str] = None,
        legacy: Optional[bool] = False,
        infer_legacy: Optional[bool] = True,
    ) -> GameMode:
        """
        Generate a formatted instance of :class: `GameMode` from stored data.

        :param yaml: A yaml dictionary in the format generated by the `to_yaml` method.
        :param legacy: Whether the dictionary will be in legacy format.
        :param infer_legacy: Whether to try to set the legacy parameter based upon the keys in the dictionary.

        :return: An instance of :class: `GameMode`.
        """
        game_mode = GameMode()
        game_mode.set_from_yaml(yaml, legacy=legacy, infer_legacy=infer_legacy)
        return game_mode

    @classmethod
    def create(
        cls,
        dict: Optional[dict] = None,
        legacy: Optional[bool] = False,
        infer_legacy: Optional[bool] = True,
        raise_errors: bool = False,
    ) -> GameMode:
        """
        Generate a formatted instance of :class: `GameMode` from stored data.

        :param dict: A nested dictionary in the format generated by the `to_dict` method.
        :param legacy: Whether the dictionary will be in legacy format.
        :param infer_legacy: Whether to try to set the legacy parameter based upon the keys in the dictionary.

        :return: An instance of :class: `GameMode`.
        """
        game_mode = GameMode()
        game_mode.set_from_dict(dict, legacy=legacy, infer_legacy=infer_legacy)
        if raise_errors and not game_mode.validation.passed:
            raise ValueError(game_mode.validation.log())
        return game_mode

    def to_dict(
        self,
        json_serializable: bool = False,
        include_none: bool = True,
        values_only: bool = False,
    ) -> dict:
        """
        Serialize the :class:`~yawning_titan.networks.network.Network` as a :class:`dict`.

        :param json_serializable: If ``True``, the :attr:`~yawning_titan.networks.network.Network`
            "d numpy array is converted to a list."
        :param include_none: Determines whether to include empty fields in the dict. Has a default
            value of ``True``.
        :return: The :class:`~yawning_titan.networks.network.Network` as a :class:`dict`.
        """
        if json_serializable:
            values_only = True
        config_dict = super().to_dict(
            values_only=values_only, include_none=include_none
        )
        if json_serializable and self.doc_metadata is not None:
            config_dict["_doc_metadata"] = self.doc_metadata.to_dict(include_none=True)

        return config_dict
