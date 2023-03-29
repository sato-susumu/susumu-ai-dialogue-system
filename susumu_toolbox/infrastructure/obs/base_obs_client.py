import logging

from susumu_toolbox.infrastructure.config import Config


# noinspection PyMethodMayBeStatic,PyShadowingNames
class BaseOBSClient:
    def __init__(self, config: Config):
        self._config = config
        self._logger = logging.getLogger(__name__)

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def set_text(self, scene_name: str, source: str, text: str) -> None:
        pass

    def set_user_utterance_text(self, text: str) -> None:
        scene_name = self._config.get_obs_scene_name()
        source_name = self._config.get_obs_user_utterance_source_name()
        self.set_text(scene_name, source_name, text)

    def set_ai_utterance_text(self, text: str) -> None:
        scene_name = self._config.get_obs_scene_name()
        source_name = self._config.get_obs_ai_utterance_source_name()
        self.set_text(scene_name, source_name, text)
