from Queue import Queue

import unittest
import speech_recognition
from speech_recognition import WavFile, AudioData

from mycroft.client.speech.listener import AudioConsumer, RecognizerLoop
from mycroft.stt import MycroftSTT
from os.path import join
from test.integrationtests.skills.skill_tester import MockSkillsLoader
from test.integrationtests.skills.discover_tests import IntentTestSequenceMeta
from mycroft.client.speech import main


#SKILL_PATH = '/opt/mycroft/skills'


class IntentTestSequence(unittest.TestCase):
    __metaclass__ = IntentTestSequenceMeta

    @classmethod
    def setUpClass(self):
        self.loader = MockSkillsLoader(SKILL_PATH)
        self.emitter = self.loader.load_skills()

    @classmethod
    def tearDownClass(self):
        self.loader.unload_skills()


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

#loader = MockSkillsLoader(SKILL_PATH)
#emitter = loader.load_skills()

#audioconsumer.queue.put(audioconsumer.create_sample_from_test_file('mycroft'))

#audioconsumer.consumer.read()
audioconsumer.queue.put(audioconsumer.create_sample_from_test_file('test'))
#audioconsumer.recognizer.set_transcriptions(["record"])
monitor = {}


def callback(m):
    monitor['utterances'] = m.get('utterances')
    print('Message', m)


audioconsumer.loop.once('recognizer_loop:utterance', callback)
audioconsumer.consumer.read()
print(monitor)

#mainMethod = main.main()
#main.handle_utterance(monitor)

print('success')
