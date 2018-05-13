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


def create_sample_from_test_file(sample_name):
    root_dir = 'voxforge'
    filename = join(
        root_dir, '1028-20100710-hne', 'wav',
        sample_name + '.wav')
    wavfile = WavFile(filename)
    with wavfile as source:
        return AudioData(
            source.stream.read(), wavfile.SAMPLE_RATE,
            wavfile.SAMPLE_WIDTH)


# create AudioConsumerTest:

# Audio files in voxforge/*/wav
# Transcription in voxforge/*/etc/PROMPTS

utterances = []
loop = RecognizerLoop()
recognizer = MockRecognizer()
queue = Queue()

consumer = AudioConsumer(
    loop.state, queue, loop, MycroftSTT(),
    loop.wakeup_recognizer,
    loop.wakeword_recognizer)


def callback(m):
    utterances.append(m.get('utterances'))


loop.on('recognizer_loop:utterance', callback)

queue.put(create_sample_from_test_file('ar-01'))
consumer.read()

queue.put(create_sample_from_test_file('ar-02'))
consumer.read()


print(utterances)


print('success')
