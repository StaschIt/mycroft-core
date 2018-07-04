from mycroft.messagebus.message import Message
from test.integrationtests.skills.skill_tester import MockSkillsLoader
from queue import Queue
import evalDataCollect

language = 'en-us'


def skill_test(utterance, expected_result):
    loader = MockSkillsLoader('/opt/mycroft/skills')
    emitter = loader.load_skills()

    s = [s for s in loader.skills if s]

    # needs any random skill?
    if s:
        s = s[0]
    else:
        raise Exception('Skill couldn\'t be loaded')

    q = Queue()
    s.emitter.q = q

    emitter.emit(
        'recognizer_loop:utterance',
        Message('recognizer_loop:utterance',
                {'utterances': [utterance]}))

    event = q.get(timeout=1)
    invoked_skill = event.data.get('intent_type').split(':')[0]
    print('invoked skill: ' + invoked_skill)
    return invoked_skill == expected_result


if __name__ == "__main__":
    utterances = evalDataCollect.read_utterances_single_dir('mycroft_en', 'test_audio/skill_test/notebook_mic')
    print('utterances', utterances)

    for key in utterances:
        expected = key.split('_')[0]

        print('bassts?', skill_test(utterances[key], expected))

    print('success')

