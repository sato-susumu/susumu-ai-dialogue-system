import time
import traceback

from loguru import logger

from susumu_ai_dialogue_system.application.base_chat_framework import BaseChatFramework
from susumu_ai_dialogue_system.infrastructure.config import Config
from susumu_ai_dialogue_system.infrastructure.stt.base_stt import STTResult, STTEvent


# noinspection PyMethodMayBeStatic,DuplicatedCode
class TextChatFramework(BaseChatFramework):
    def __init__(self, config: Config):
        super().__init__(config)

        self._stt.event_subscribe(STTEvent.START, self._on_stt_start)
        self._stt.event_subscribe(STTEvent.END, self._on_stt_end)
        self._stt.event_subscribe(STTEvent.RESULT, self._on_stt_result)
        self._stt.event_subscribe(STTEvent.DEBUG_MESSAGE, self._on_stt_debug_message)
        self._stt.event_subscribe(STTEvent.ERROR, self._on_stt_error)

    def _on_stt_result(self, result: STTResult):
        super()._on_stt_result(result)
        self._obs.set_user_utterance_text(result.text)

    def run_once(self) -> None:
        super().run_once()
        # noinspection PyBroadException
        try:
            self._connect_all()

            while self._chat.is_connecting() and not self._termination_flag.is_set():
                time.sleep(1)

            while self._chat.is_connected() and not self._termination_flag.is_set():
                ai_result = self._wait_ai_response()
                if ai_result is None:
                    break

                if self._tts.is_playing():
                    logger.debug("前の音声合成が再生中なので、再生停止")
                    self._tts.tts_stop()

                ai_text = ai_result.text
                self._present_ai_message(ai_text, obs_ai_utterance_text=ai_text)

                quick_replies = ai_result.quick_replies
                self._present_quick_replies(quick_replies)

                user_text = self._wait_user_input()
                if user_text == "bye" or self._termination_flag.is_set():
                    self._termination_flag.set()
                    break

                self._request_ai_message(user_text=user_text, obs_ai_utterance_text="(考え中。。。)")
        except Exception:
            logger.error(traceback.format_exc())  # いつものTracebackが表示される
            logger.info("エラーが発生しましたが処理を継続します！")
        finally:
            self._disconnect_all()


if __name__ == "__main__":
    _config = Config()
    _config.search_and_load()
    TextChatFramework(_config).run_forever()
