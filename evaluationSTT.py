#!/usr/bin/env python
# -*- coding: iso-8859-1 -*

from multiprocessing import Queue
import os
import time
import speech_recognition
from speech_recognition import WavFile, AudioData
from mycroft.client.speech.listener import AudioConsumer, RecognizerLoop
import mycroft.stt
from os.path import join
import editdistance
import codecs

speechdata_path = 'test_audio/smallVoxforge/en/1028-20100710-hne'

mycroft_stt = mycroft.stt.MycroftSTT()
deepspeech_stt = mycroft.stt.DeepSpeechServerSTT()

wav_durs = []
wav_readtimes = []


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


def wav_duration(filepath):
    import wave
    import contextlib
    with contextlib.closing(wave.open(filepath, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration


def create_sample_from_test_file(sample_path):
    wavfile = WavFile(sample_path)
    with wavfile as source:
        return AudioData(
            source.stream.read(), wavfile.SAMPLE_RATE,
            wavfile.SAMPLE_WIDTH)


def create_utterances_from_wavfiles(directory, stt_string):
    stt = stt_string.split('_')[0]
    lang = stt_string.split('_')[1]
    utterances = {}
    loop = RecognizerLoop()
    queue = Queue()

    if 'de' in lang:
        mycroft_stt.lang = 'de'
        deepspeech_stt.lang = 'de'
    elif 'en' in lang:
        mycroft_stt.lang = 'en-us'
        deepspeech_stt.lang = 'en-us'

    consumer = AudioConsumer(
        loop.state, queue, loop, (mycroft_stt if 'mycroft' in stt else deepspeech_stt),
        loop.wakeup_recognizer,
        loop.wakeword_recognizer)

    wavfiles = (x for x in os.listdir(directory) if x.endswith('.wav'))
    for wavfile in wavfiles:
        print('wavfile: ' + wavfile)
        begin_time = time.time()

        def callback(m):
            utterances[wavfile.replace('.wav', '')] = m.get('utterances')[0].upper()

        loop.on('recognizer_loop:utterance', callback)

        queue.put(create_sample_from_test_file(join(directory, wavfile)))
        consumer.read()
        end_time = time.time()

        # for plotting
        wav_durs.append(wav_duration(join(directory, wavfile)))
        wav_readtimes.append(end_time - begin_time)

    return utterances


def create_transcriptions_from_file(prompt_file):
    transcriptions = {}

    lines = [line.rstrip('\n') for line in codecs.open(prompt_file, 'r', 'utf-8')]

    for line in lines:
        split = line.split('/')
        transcriptions[split[-1].split(' ', 1)[0]] = split[-1].split(' ', 1)[1].upper()

    return transcriptions


def total_edit_distance(dic1, dic2, mistakeoutput=None):
    string1 = ''
    string2 = ''
    mistakes = ''
    for key in dic1:
        if editdistance.eval(dic1[key], dic2[key]) > 0:
            mistakes += 'Understood:\n' + dic1[key] + '\nbut was:\n' + dic2[key] + '\n\n'

        string1 += ' ' + dic1[key]
        string2 += ' ' + dic2[key]

    if mistakeoutput is not None:
        f = codecs.open(mistakeoutput + '_mistakes.txt', 'w', 'utf-8')
        print(mistakes)
        f.write(mistakes)
    return editdistance.eval(string1, string2) * 1.0 / max(len(string1), len(string2))


def wer(s1, s2):
    s1 = s1.split()
    s2 = s2.split()
    words = list(set([w for w in s1 + s2]))
    s1 = [words.index(w) for w in s1]
    s2 = [words.index(w) for w in s2]
    return editdistance.eval(s1, s2) * 1.0 / max(len(s1), len(s2))


def total_wer(dic1, dic2):
    string1 = ''
    string2 = ''

    for key in dic1:
        string1 += ' ' + dic1[key]
        string2 += ' ' + dic2[key]

    return wer(string1, string2)


def sentence_error_rate(dic1, dic2):
    correct = 0
    total = 0

    for key in dic1:
        total += 1
        if editdistance.eval(dic1[key], dic2[key]) == 0:
            correct += 1
    return 1 - (correct * 1.0 / total)


if __name__ == "__main__":
    # Audio files in voxforge/*/wav
    # Transcription in voxforge/*/etc/PROMPTS

    utterances_dic = create_utterances_from_wavfiles(join(speechdata_path, 'wav'), 'mycroft_en')
    transcriptions_dic = create_transcriptions_from_file(join(speechdata_path, 'etc', 'PROMPTS'))

    print(utterances_dic)
    print('character distance', total_edit_distance(utterances_dic, transcriptions_dic))
    print('success')
