from susumu_toolbox.infrastructure.config import Config
from susumu_toolbox.infrastructure.pyaudio_player import PyAudioPlayer
from susumu_toolbox.infrastructure.tts.base_tts import BaseTTS


class DummyTTS(BaseTTS):
    def __init__(self, config: Config):
        super().__init__(config)
        self._config = config
        self._player = PyAudioPlayer(config)

    def tts_play_sync(self, text: str) -> None:
        super().tts_play_sync(text)

    def tts_play_async(self, text: str) -> None:
        super().tts_play_async(text)
