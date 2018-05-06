from Queue import Queue

import speech_recognition
from os.path import dirname, join
from speech_recognition import WavFile, AudioData

from mycroft.client.speech.listener import AudioConsumer, RecognizerLoop
from mycroft.stt import MycroftSTT

from mycroft.skills.core import MycroftSkill


class MockRecognizer(object):
    def __init__(self):
        self.transcriptions = []

    def recognize_mycroft(self, audio, key=None,
                          language=None, show_all=False):
        if len(self.transcriptions) > 0:
            return self.transcriptions.pop(0)
        else:
            raise speech_recognition.UnknownValueError()

    def set_transcriptions(self, transcriptions):
        self.transcriptions = transcriptions


class AudioConsumerTest:
    """
    AudioConsumerTest
    """

    def setUp(self):
        self.loop = RecognizerLoop()
        self.queue = Queue()
        self.recognizer = MockRecognizer()
        self.consumer = AudioConsumer(
            self.loop.state, self.queue, self.loop, MycroftSTT(),
            self.loop.wakeup_recognizer,
            self.loop.wakeword_recognizer)

    def create_sample_from_test_file(self, sample_name):
        root_dir = 'test'
        filename = join(
            root_dir, 'unittests', 'client',
            'data', sample_name + '.wav')
        wavfile = WavFile(filename)
        with wavfile as source:
            return AudioData(
                source.stream.read(), wavfile.SAMPLE_RATE,
                wavfile.SAMPLE_WIDTH)


audioconsumer = AudioConsumerTest()
audioconsumer.setUp()

audioconsumer.queue.put(audioconsumer.create_sample_from_test_file('mycroft'))

audioconsumer.consumer.read()
audioconsumer.queue.put(audioconsumer.create_sample_from_test_file('mycroft'))
audioconsumer.recognizer.set_transcriptions(["record"])
monitor = {}

def callback(m):
    monitor['utterances'] = m.get('utterances')
    print(m)

audioconsumer.loop.once('recognizer_loop:utterance', callback)
audioconsumer.consumer.read()
print(monitor)

print('success')
