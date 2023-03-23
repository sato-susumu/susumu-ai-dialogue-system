import time
import traceback

from six.moves import queue

from susumu_toolbox.application.base_chat_sample import BaseChatSample
from susumu_toolbox.infrastructure.chat.base_chat import ChatResult
from susumu_toolbox.infrastructure.config import Config
from susumu_toolbox.infrastructure.stt.base_stt import STTResult
from susumu_toolbox.infrastructure.stt.sr_google_sync_stt import SRGoogleSyncSTT
from susumu_toolbox.infrastructure.system_setting import SystemSettings


# noinspection PyMethodMayBeStatic,DuplicatedCode
class VoiceChatSample(BaseChatSample):
    def __init__(self, config: Config, system_settings: SystemSettings):
        super().__init__(config, system_settings)

        self._chat_message_queue = queue.Queue()
        self._stt_message_queue = queue.Queue()
        self._chat = self.create_chat()
        self._chat.subscribe(self._chat.EVENT_CHAT_OPEN, self._on_chat_open)
        self._chat.subscribe(self._chat.EVENT_CHAT_CLOSE, self._on_chat_close)
        self._chat.subscribe(self._chat.EVENT_CHAT_MESSAGE, self._on_chat_message)
        self._chat.subscribe(self._chat.EVENT_CHAT_ERROR, self._on_chat_error)

        speech_contexts = ["後退", "前進", "右旋回", "左旋回", "バック"]

        self._stt = self.create_stt(speech_contexts=speech_contexts)
        self._stt.subscribe(self._stt.EVENT_STT_START, self._on_stt_start)
        self._stt.subscribe(self._stt.EVENT_STT_END, self._on_stt_end)
        self._stt.subscribe(self._stt.EVENT_STT_RESULT, self._on_stt_result)
        self._stt.subscribe(self._stt.EVENT_STT_DEBUG_MESSAGE, self._on_stt_debug_message)
        self._stt.subscribe(self._stt.EVENT_STT_ERROR, self._on_stt_error)

        self._tts = self.create_tts()

        self._translator = self.create_translator()

        self._obs = self.create_obs_client()

    def _on_chat_open(self):
        print("_on_chat_open")

    def _on_chat_close(self, status_code, close_msg):
        print(f"_on_chat_close status_code={status_code} close_msg={close_msg}")
        self._chat_message_queue.put(None)

    def _on_chat_message(self, message: ChatResult):
        print("_on_chat_message")
        self._chat_message_queue.put(message)

    def _on_chat_error(self, error: Exception):
        print(f"_on_chat_error exception={error}")

    def _on_stt_start(self):
        if type(self._stt) == SRGoogleSyncSTT:
            message = "ME(マイクに向かって何か5文字以上話してください): "
        else:
            message = "ME(マイクに向かって何か話してください): "
        print(message)
        self._obs.set_user_utterance_text(message)

    def _on_stt_end(self):
        print("音声認識 終了")

    def _on_stt_result(self, result: STTResult):
        if result.is_final:
            if result.is_timed_out:
                print('stt final(timeout):' + result.text)
            else:
                print('stt final:' + result.text)
            self._stt_message_queue.put(result)
        else:
            print('stt not final:' + result.text)

        self._obs.set_user_utterance_text(result.text)

    def _on_stt_debug_message(self, x):
        # # デバッグ出力
        # print("------------------")
        # print(x)
        pass

    def _on_stt_error(self, e):
        print(e)

    def _wait_input(self) -> str:
        while True:
            if type(self._stt) == SRGoogleSyncSTT:
                print("音声認識 準備中")
            self._stt.recognize()
            print("STTメッセージキュー待機")
            stt_message = self._stt_message_queue.get(block=True, timeout=None)
            print("STTメッセージキュー取得")
            if stt_message is None:
                return "bye"
            input_text = stt_message.text
            if input_text == "終了":
                return "bye"
            if input_text == "":
                print("音声認識 失敗")
                continue
            return input_text

    def run_once(self) -> None:
        # noinspection PyBroadException
        try:
            self._obs.connect()
            self._obs.set_user_utterance_text("")
            self._obs.set_ai_utterance_text("")
            self._chat.connect()

            while self._chat.is_connecting():
                time.sleep(1)

            while self._chat.is_connected():
                print("CHATメッセージキュー待機")
                chat_message = self._chat_message_queue.get(block=True, timeout=None)
                print("CHATメッセージキュー取得")
                if chat_message is None:
                    break
                message_text = chat_message.text
                message_text = self._translator.translate(message_text, self._translator.LANG_CODE_JA_JP)
                print("Bot: " + message_text)
                self._obs.set_ai_utterance_text(message_text)
                self._tts.tts_play_sync(message_text)

                input_text = self._wait_input()

                self._obs.set_ai_utterance_text("(考え中。。。)")
                if input_text == "bye":
                    self._chat.disconnect()
                else:
                    text = self._translator.translate(input_text, self._translator.LANG_CODE_EN_US)
                    print("Bot 返事待ち開始")
                    self._chat.send_message(text)
                    print("Bot 返事待ち完了 ")
        except Exception:
            print(traceback.format_exc())  # いつものTracebackが表示される
            print("エラーが発生しましたが処理を継続します！")
        finally:
            self._obs.set_user_utterance_text("")
            self._obs.set_ai_utterance_text("")
            self._obs.disconnect()
            self._chat.disconnect()

    def run_forever(self) -> None:
        print("run_forever")
        while True:
            self.run_once()


if __name__ == "__main__":
    _config = Config()
    _config.search_and_load()
    _system_settings = SystemSettings(_config)
    VoiceChatSample(_config, _system_settings).run_forever()