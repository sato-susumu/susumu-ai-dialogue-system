from __future__ import annotations

import webbrowser
from typing import TYPE_CHECKING

import PySimpleGUI as Sg
from PySimpleGUI import Window

from susumu_toolbox.infrastructure.config import Config

if TYPE_CHECKING:
    from susumu_toolbox.ui.main_window import MainWindow


class BaseLayout:
    INPUT_SIZE_SHORT = (8, 1)
    INPUT_SIZE_NORMAL = (20, 1)
    INPUT_SIZE_LONG = (70, 1)
    BUTTON_SIZE_NORMAL = (10, 1)

    def __init__(self, config: Config):
        self._config = config

    @classmethod
    def get_key(cls) -> str:
        raise NotImplementedError

    def get_layout(self):
        raise NotImplementedError

    def update_layout(self, window: Window) -> None:
        raise NotImplementedError

    def handle_event(self, event, values, main_window: MainWindow) -> None:
        raise NotImplementedError

    def update_config(self, config: Config) -> None:
        self._config = config

    def is_linked_text_event(self, event) -> bool:
        if event.startswith("URL "):
            return True
        return False

    # noinspection PyMethodMayBeStatic
    def open_linked_text_url(self, event):
        url = event.split(' ')[1]
        webbrowser.open(url)

    # noinspection PyMethodMayBeStatic
    def create_linked_text(self, text: str, url: str):
        font = ('Arial', 10, "underline")
        return Sg.Text(text, tooltip=url, enable_events=True, font=font, key=f'URL {url}',
                       pad=(0, 0), text_color="blue")