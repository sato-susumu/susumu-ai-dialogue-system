from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from susumu_toolbox.ui.settings_layout import SettingsLayout
    from susumu_toolbox.ui.main_window import MainWindow

import PySimpleGUI as Sg
from PySimpleGUI import Window
from loguru import logger

from susumu_toolbox.application.common.tts_test import TTSTest
from susumu_toolbox.infrastructure.config import Config, OutputFunction
from susumu_toolbox.ui.base_layout import BaseLayout
from susumu_toolbox.ui.gui_events import GuiEvents


# noinspection PyMethodMayBeStatic
class SettingsTtsTabLayout(BaseLayout):
    _VOICEVOX_SPEAKER_COMBO_KEY = 'voicevox_speaker_combo_key'
    # VOICEVOXのスピーカーリスト。
    # TODO: 選択した名前はconfigに保存し、Windowに表示する。設定ボタンを追加し、押したときに動的にスピーカーを取得する
    _voicevox_speaker_dic = {'四国めたん-ノーマル': 2, '四国めたん-あまあま': 0, '四国めたん-ツンツン': 6,
                             '四国めたん-セクシー': 4, '四国めたん-ささやき': 36, '四国めたん-ヒソヒソ': 37,
                             'ずんだもん-ノーマル': 3, 'ずんだもん-あまあま': 1, 'ずんだもん-ツンツン': 7,
                             'ずんだもん-セクシー': 5, 'ずんだもん-ささやき': 22, 'ずんだもん-ヒソヒソ': 38,
                             '春日部つむぎ-ノーマル': 8, '雨晴はう-ノーマル': 10, '波音リツ-ノーマル': 9,
                             '玄野武宏-ノーマル': 11, '玄野武宏-喜び': 39, '玄野武宏-ツンギレ': 40,
                             '玄野武宏-悲しみ': 41, '白上虎太郎-ふつう': 12, '白上虎太郎-わーい': 32,
                             '白上虎太郎-びくびく': 33, '白上虎太郎-おこ': 34, '白上虎太郎-びえーん': 35,
                             '青山龍星-ノーマル': 13, '冥鳴ひまり-ノーマル': 14, '九州そら-ノーマル': 16,
                             '九州そら-あまあま': 15, '九州そら-ツンツン': 18, '九州そら-セクシー': 17,
                             '九州そら-ささやき': 19, 'もち子さん-ノーマル': 20, '剣崎雌雄-ノーマル': 21,
                             'WhiteCUL-ノーマル': 23, 'WhiteCUL-たのしい': 24, 'WhiteCUL-かなしい': 25,
                             'WhiteCUL-びえーん': 26, '後鬼-人間ver.': 27, '後鬼-ぬいぐるみver.': 28,
                             'No.7-ノーマル': 29, 'No.7-アナウンス': 30, 'No.7-読み聞かせ': 31,
                             'ちび式じい-ノーマル': 42, '櫻歌ミコ-ノーマル': 43,
                             '櫻歌ミコ-第二形態': 44, '櫻歌ミコ-ロリ': 45, '小夜/SAYO-ノーマル': 46,
                             'ナースロボ＿タイプＴ-ノーマル': 47, 'ナースロボ＿タイプＴ-楽々': 48,
                             'ナースロボ＿タイプＴ-恐怖': 49, 'ナースロボ＿タイプＴ-内緒話': 50}

    def __init__(self, config: Config, settings_layout: SettingsLayout):
        super().__init__(config)
        self._settings_layout = settings_layout

    @classmethod
    def get_key(cls) -> str:
        raise "settings_tts_tab_layout"

    def get_layout(self):
        default_speaker_no = self._config.get_voicevox_speaker_no()
        default_speaker_key = [k for k, v in self._voicevox_speaker_dic.items() if v == default_speaker_no][0]

        voicevox_items = [
            [Sg.Text('・利用にはVOICEVOXの起動が必要です。')],
            [Sg.Text('アドレス'),
             Sg.InputText(default_text=self._config.get_voicevox_host(),
                          key=self._config.KEY_VOICEVOX_HOST,
                          size=self.INPUT_SIZE_NORMAL,
                          ),
             ],
            [Sg.Text('ポート番号'),
             Sg.InputText(default_text=self._config.get_voicevox_port_no(),
                          key=self._config.KEY_VOICEVOX_PORT_NO,
                          size=self.INPUT_SIZE_SHORT,
                          enable_events=True,
                          ),
             ],
            [Sg.Combo(list(self._voicevox_speaker_dic.keys()),
                      default_value=default_speaker_key,
                      key=self._VOICEVOX_SPEAKER_COMBO_KEY,
                      size=(30, 1),
                      readonly=True,
                      ),
             ],
            [Sg.Button("テスト", size=(15, 1), key=GuiEvents.VOICEVOX_TEST)],
        ]

        gtts_items = [
            [Sg.Button("テスト", size=(15, 1), key=GuiEvents.GTTS_TEST)],
        ]

        pyttsx3_items = [
            [Sg.Button("テスト", size=(15, 1), key=GuiEvents.PYTTSX3_TEST)],
        ]

        google_cloud_tts_items = [
            [Sg.Text('・利用には別途GCP認証もしくは下記APIキーの設定が必要です。')],
            [Sg.Text('Google Text-to-SpeechのAPIキー'),
             Sg.InputText(default_text=self._config.get_gcp_text_to_speech_api_key(),
                          key=self._config.KEY_GCP_TEXT_TO_SPEECH_API_KEY,
                          password_char="*",
                          size=self.INPUT_SIZE_LONG,
                          )
             ],
            [Sg.Button("テスト", size=(15, 1), key=GuiEvents.GOOGLE_CLOUD_TTS_TEST)],
        ]

        tts_tab_layout = [
            [Sg.Frame("gTTS 音声合成(動作確認用)", gtts_items, expand_x=True)],
            [Sg.Frame("VOICEVOX 音声合成", voicevox_items, expand_x=True)],
            [Sg.Frame("Google Text-to-Speech 音声合成", google_cloud_tts_items, expand_x=True)],
            [Sg.Frame("Pyttsx3 音声合成", pyttsx3_items, expand_x=True)],
        ]
        return tts_tab_layout

    def update_layout(self, window: Window) -> None:
        pass

    def __tts_test(self, event, values) -> None:
        config = self._config.clone()
        config = self._settings_layout.update_local_config_by_values(values, config)

        if event == GuiEvents.VOICEVOX_TEST:
            config.set_common_output_function(OutputFunction.VOICEVOX)
        elif event == GuiEvents.GTTS_TEST:
            config.set_common_output_function(OutputFunction.GTTS)
        elif event == GuiEvents.GOOGLE_CLOUD_TTS_TEST:
            config.set_common_output_function(OutputFunction.GOOGLE_CLOUD)
        elif event == GuiEvents.PYTTSX3_TEST:
            config.set_common_output_function(OutputFunction.PYTTSX3)
        else:
            raise Exception("想定外のイベントです")

        try:
            TTSTest(config).run()
        except Exception as e:
            logger.error(e)
            Sg.PopupError(e, title="エラー", keep_on_top=True)

    def get_selected_speaker_no(self, values):
        selected_speaker_key = values[self._VOICEVOX_SPEAKER_COMBO_KEY]
        return self._voicevox_speaker_dic[selected_speaker_key]

    def handle_event(self, event, values, main_window: MainWindow) -> None:
        if event in (self._config.KEY_VOICEVOX_PORT_NO, self._config.KEY_VOICEVOX_SPEAKER_NO):
            main_window.input_validation_number_only(event, values)

        if event in (
                GuiEvents.VOICEVOX_TEST, GuiEvents.GTTS_TEST, GuiEvents.GOOGLE_CLOUD_TTS_TEST,
                GuiEvents.PYTTSX3_TEST):
            self.__tts_test(event, values)