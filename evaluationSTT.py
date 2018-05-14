from Queue import Queue

import os
import sys
import speech_recognition
from speech_recognition import WavFile, AudioData

from mycroft.client.speech.listener import AudioConsumer, RecognizerLoop
from mycroft.stt import MycroftSTT
from os.path import join
import editdistance

speechdata_path = sys.argv[1]


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


def create_utterances_from_wavfiles(directory):
    utterances = {}
    loop = RecognizerLoop()
    queue = Queue()

    consumer = AudioConsumer(
        loop.state, queue, loop, MycroftSTT(),
        loop.wakeup_recognizer,
        loop.wakeword_recognizer)

    for wavfile in os.listdir(directory):
        def callback(m):
            utterances[wavfile.replace('.wav', '')] = m.get('utterances')[0].upper()

        loop.on('recognizer_loop:utterance', callback)

        queue.put(create_sample_from_test_file(join(directory, wavfile)))
        consumer.read()

    return utterances


def create_transcriptions_from_file(prompt_file):
    transcriptions = {}

    lines = [line.rstrip('\n') for line in open(prompt_file)]

    for line in lines:
        split = line.split('/')
        transcriptions[split[-1].split(' ', 1)[0]] = split[-1].split(' ', 1)[1].decode('unicode-escape')

    return transcriptions


def total_edit_distance(dic1, dic2):
    distance = 0
    for key in dic1:
        # if editdistance.eval(dic1[key], dic2[key]) > 0:
        #     print('Mistake! Understood: ' + dic1[key] + ' but was: ' + dic2[key])
        distance += editdistance.eval(dic1[key], dic2[key])

    return distance


# Audio files in voxforge/*/wav
# Transcription in voxforge/*/etc/PROMPTS

utterances_dic = create_utterances_from_wavfiles(join(speechdata_path, 'wav'))
transcriptions_dic = create_transcriptions_from_file(join(speechdata_path, 'etc', 'PROMPTS'))

print('distance', total_edit_distance(utterances_dic, transcriptions_dic))

# print (utterances_dic, transcriptions_dic)

print('success')
