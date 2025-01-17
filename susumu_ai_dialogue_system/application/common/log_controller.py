from susumu_ai_dialogue_system.application.common.log_mannager import LogManager
from susumu_ai_dialogue_system.infrastructure.config import Config


class LogController:
    def __init__(self, config: Config):
        self._config = config
        LogManager().setup_logger(self._config.get_advanced_console_log_level())

    def update_config(self, config: Config):
        self._config = config
        LogManager().setup_logger(self._config.get_advanced_console_log_level())
