from __future__ import annotations

from typing import TYPE_CHECKING

import PySimpleGUI as Sg

if TYPE_CHECKING:
    from susumu_ai_dialogue_system.ui.settings_layout import SettingsLayout
    from susumu_ai_dialogue_system.ui.main_window import MainWindow

from susumu_ai_dialogue_system.infrastructure.config import Config
from susumu_ai_dialogue_system.ui.base_layout import BaseLayout


# noinspection PyMethodMayBeStatic
class SettingsAiTabLayout(BaseLayout):
    def __init__(self, config: Config, settings_layout: SettingsLayout, main_window: MainWindow):
        super().__init__(config, main_window)
        self._settings_layout = settings_layout
        self.__current_ai_id = config.get_ai_id_list()[0]

    @classmethod
    def get_key(cls) -> str:
        raise "settings_ai_tab_layout"

    def get_layout(self):
        ai_tab_layout = [
            [Sg.Text('プロンプト')],
            [Sg.Multiline(
                default_text=self._config.get_ai_system_settings_text(self.__current_ai_id),
                key=self._config.KEY_AI_SYSTEM_SETTINGS_TEXT,
                expand_x=True,
                expand_y=True,
                enable_events=True,
            )]
        ]

        return ai_tab_layout

    def get_current_ai_id(self) -> str:
        return self.__current_ai_id

    def handle_event(self, event, values) -> None:
        match event:
            case self._config.KEY_AI_SYSTEM_SETTINGS_TEXT:
                self._config.set_ai_system_settings_text(self.get_current_ai_id(),
                                                         values[self._config.KEY_AI_SYSTEM_SETTINGS_TEXT])
