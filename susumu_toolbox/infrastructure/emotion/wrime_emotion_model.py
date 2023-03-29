import logging

import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from susumu_toolbox.infrastructure.config import Config
from susumu_toolbox.infrastructure.emotion.base_emotion_model import BaseEmotionModel
from susumu_toolbox.infrastructure.emotion.emotion import Emotion


# noinspection PyMethodMayBeStatic
class WrimeEmotionModel(BaseEmotionModel):
    def __init__(self, config: Config):
        super().__init__(config)

        # noinspection SpellCheckingInspection
        checkpoint = 'cl-tohoku/bert-base-japanese-whole-word-masking'
        self._tokenizer = AutoTokenizer.from_pretrained(checkpoint)

        # self._emotion_names_jp = ['喜び', '悲しみ', '期待', '驚き', '怒り', '恐れ', '嫌悪', '信頼']
        self._emotion_names = ['Joy', 'Sadness', 'Anticipation', 'Surprise', 'Anger', 'Fear', 'Disgust', 'Trust']
        num_labels = len(self._emotion_names)
        model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=num_labels)

        self._model = model.from_pretrained(self._config.get_wrime_model_dir_path())
        # 推論モード
        self._model.eval()

    def get_max_emotion(self, text: str) -> (Emotion, float, dict):
        result_dict, raw_dict = self.get_emotion(text)
        max_emotion = max(result_dict, key=result_dict.get)
        return max_emotion, result_dict[max_emotion], result_dict

    def get_emotion(self, text: str) -> (dict, dict):
        result_dict = self.get_raw_emotion(text)
        return self._convert_emotion_dict(result_dict), result_dict

    def _convert_emotion_dict(self, in_dict: dict):
        out_dict = {
            Emotion.HAPPY: max(in_dict.get('Joy'), in_dict.get('Trust')),
            Emotion.SAD: max(in_dict.get('Sadness'), in_dict.get('Fear')),
            Emotion.SURPRISED: in_dict.get('Surprise'),
            Emotion.ANGRY: in_dict.get('Anger'),
            Emotion.RELAXED: 0.0,
        }
        return out_dict

    def _np_softmax(self, x):
        f_x = np.exp(x) / np.sum(np.exp(x))
        return f_x

    def get_raw_emotion(self, text: str) -> dict:
        tokens = self._tokenizer(text, truncation=True, return_tensors="pt")
        tokens.to(self._model.device)
        predictions = self._model(**tokens)
        probability = self._np_softmax(predictions.logits.cpu().detach().numpy()[0])
        raw_emotion_dict = {n: p for n, p in zip(self._emotion_names, probability)}
        return raw_emotion_dict


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    _logger = logging.getLogger(__name__)
    _config = Config()
    _config.set_wrime_model_dir_path("../../../model_data/wrime_model.pth")
    if not _config.exists_wrime_model_dir():
        raise FileNotFoundError("WRIME model not found.")
    _model = WrimeEmotionModel(_config)


    def func(text: str):
        out_dict, raw_dict = _model.get_emotion(text)
        max_key = max(out_dict, key=out_dict.get)
        max_value = out_dict[max_key]
        _logger.debug(text)
        _logger.debug(out_dict)
        _logger.debug(raw_dict)
        _logger.debug(max_key, max_value)
        _logger.debug("")


    func("大好きな人が遠くへ行ってしまった")
    func("誰がこんなことをしたんだ！？もう許せない。")
    func("いい加減にしてくれ！もう限界だ！")
    func("何度も言ってるのに、何も聞いてくれない。もう腹が立つ！")
    func("喧嘩したけど仲直りできた！")
    func("友達と喧嘩した。泣きそう。")
    func("我慢せずに食べまくる。倍返しだ。")
    func("好きなアーティストのコンサートだったのに。。。")
    func("私が立ち上がった時、世界は回っていると思った。後で気がついたら、私が回っていたのだとわかった。")
    func('もう怒った!')
    func('ああ、もうやだ')
    func('頼りになりますね！')
