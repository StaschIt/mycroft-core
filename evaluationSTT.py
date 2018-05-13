from Queue import Queue

import speech_recognition
from speech_recognition import WavFile, AudioData

from mycroft.client.speech.listener import AudioConsumer, RecognizerLoop
from mycroft.stt import MycroftSTT
from os.path import join


class MockRecognizer(object):
    def __init__(self):
        self.transcriptions = []

    def recognize_mycroft(self):
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

    def __init__(self):
        self.loop = RecognizerLoop()
        self.queue = Queue()
        self.recognizer = MockRecognizer()
        self.consumer = AudioConsumer(
            self.loop.state, self.queue, self.loop, MycroftSTT(),
            self.loop.wakeup_recognizer,
            self.loop.wakeword_recognizer)

    def create_sample_from_test_file(self, sample_name):
        root_dir = 'voxforge'
        filename = join(
            root_dir, '1028-20100710-hne', 'wav',
            sample_name + '.wav')
        wavfile = WavFile(filename)
        with wavfile as source:
            return AudioData(
                source.stream.read(), wavfile.SAMPLE_RATE,
                wavfile.SAMPLE_WIDTH)


# Audio files in voxforge/*/wav
# Transcription in voxforge/*/etc/PROMPTS

audioconsumer = AudioConsumerTest()


audioconsumer.queue.put(audioconsumer.create_sample_from_test_file('ar-01'))
audioconsumer.queue.put(audioconsumer.create_sample_from_test_file('ar-02'))
monitor = {}


def callback(m):
    monitor['utterances'] = m.get('utterances')


audioconsumer.loop.once('recognizer_loop:utterance', callback)
audioconsumer.consumer.read()
print(monitor)


print('success')
