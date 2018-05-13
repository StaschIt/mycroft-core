from Queue import Queue

import os
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


def create_sample_from_test_file(sample_path):

    wavfile = WavFile(sample_path)
    with wavfile as source:
        return AudioData(
            source.stream.read(), wavfile.SAMPLE_RATE,
            wavfile.SAMPLE_WIDTH)


def create_utterance_list(directory):
    utterances = {}
    loop = RecognizerLoop()
    queue = Queue()

    consumer = AudioConsumer(
        loop.state, queue, loop, MycroftSTT(),
        loop.wakeup_recognizer,
        loop.wakeword_recognizer)

    for wavfile in os.listdir(directory):
        def callback(m):
            utterances[wavfile] = m.get('utterances')

        loop.on('recognizer_loop:utterance', callback)

        queue.put(create_sample_from_test_file(join(directory, wavfile)))
        consumer.read()

    return utterances


# Audio files in voxforge/*/wav
# Transcription in voxforge/*/etc/PROMPTS

print(create_utterance_list(join('voxforge', '1028-20100710-hne', 'wav')))


print('success')
