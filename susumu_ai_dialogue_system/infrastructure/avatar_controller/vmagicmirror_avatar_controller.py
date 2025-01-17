import mido
import mido.backends.rtmidi  # noqa

from susumu_ai_dialogue_system.infrastructure.avatar_controller.base_avatar_controller import BaseAvatarController
from susumu_ai_dialogue_system.infrastructure.config import Config
from susumu_ai_dialogue_system.infrastructure.emotion.emotion import Emotion


# noinspection PyMethodMayBeStatic
class VMagicMirrorController(BaseAvatarController):
    _mapping = {
        Emotion.HAPPY: 60,
        Emotion.SAD: 61,
        Emotion.SURPRISED: 62,
        Emotion.ANGRY: 63,
        Emotion.RELAXED: 64,
    }

    def __init__(self, config: Config):
        super().__init__(config)

        self._mido_output = None

    def _get_loop_midi_output_port_mame(self) -> str:
        # noinspection PyUnresolvedReferences
        port_name_list = mido.get_output_names()
        # TODO: デバッグログで出力する
        # logger.debug(port_name_list)

        # "loopMIDI"を含む最初の要素を取得する
        loop_midi_port = next((s for s in port_name_list if 'loopMIDI' in s), None)

        if loop_midi_port is None:
            raise Exception("loopMIDI not found")
        return loop_midi_port

    def connect(self):
        if self._mido_output:
            return

        port_name = self._get_loop_midi_output_port_mame()
        # noinspection PyUnresolvedReferences
        self._mido_output = mido.open_output(port_name)

    def disconnect(self):
        if self._mido_output is None:
            return
        self._mido_output.close()
        self._mido_output = None

    def set_emotion(self, emotion: Emotion):
        if emotion == Emotion.NEUTRAL:
            return
        note = self._mapping[emotion]
        msg = mido.Message('note_on', note=note, velocity=127, time=0)
        # TODO: デバッグログで出力する
        # logger.debug("Sending message: {}".format(msg))
        self._mido_output.send(msg)


if __name__ == '__main__':
    import random
    from time import sleep

    _config = Config()
    _controller = VMagicMirrorController(_config)
    _controller.connect()
    try:
        while True:
            _emotion = random.choice(list(Emotion))
            _controller.set_emotion(_emotion)
            sleep(1)
    finally:
        _controller.disconnect()
