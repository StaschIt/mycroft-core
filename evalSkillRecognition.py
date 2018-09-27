from mycroft.messagebus.message import Message
from test.integrationtests.skills.skill_tester import MockSkillsLoader
from queue import Queue
import evalDataCollect
import codecs


def prepare(skill_dir):
    loader = MockSkillsLoader(skill_dir)
    emitter = loader.load_skills()
    return emitter, [s for s in loader.skills if s]


def envoked_skill(utterance, lang):
    (emitter, skill) = prepare('/opt/mycroft/skills')

    # needs any random skill?
    if skill:
        skill = skill[0]
    else:
        raise Exception('Skill couldn\'t be loaded')

    q = Queue()
    skill.emitter.q = q

    emitter.emit(
        'recognizer_loop:utterance',
        Message('recognizer_loop:utterance',
                {'utterances': [utterance], 'lang': lang}))

    event = q.get(timeout=1)
    try:
        invoked_skill = event.data.get('intent_type').split(':')[0]
        print(invoked_skill)
    except AttributeError:
        # no skill were found
        print('no skill found')
        return False


def skill_test(utterance, expected_result, lang):
    (emitter, skill) = prepare('/opt/mycroft/skills')

    # needs any random skill?
    if skill:
        skill = skill[0]
    else:
        raise Exception('Skill couldn\'t be loaded')

    q = Queue()
    skill.emitter.q = q

    emitter.emit(
        'recognizer_loop:utterance',
        Message('recognizer_loop:utterance',
                {'utterances': [utterance], 'lang': lang}))

    event = q.get(timeout=1)
    try:
        invoked_skill = event.data.get('intent_type').split(':')[0]
        print('invoked skill: ' + invoked_skill)
        if invoked_skill != expected_result:
            append_line_to_file('skilltest-failure',
                                'Fail for utterance \'' + utterance + '\'. expected: ' + expected_result + ' but was: '
                                + invoked_skill)
            return False
        else:
            append_line_to_file('skilltest-success', 'utterance ' + utterance + ' calls ' + invoked_skill)
            return True
    except AttributeError:
        # no skill were found
        append_line_to_file('skilltest-failure',
                            'no skill found for utterance ' + utterance + '. Expected skill: ' + expected_result)
        return False


def append_line_to_file(file, text):
    f = codecs.open(file, 'a', 'utf-8')
    f.write(text + '\n')


def wav_eval(stt, directory, language):
    utterances = evalDataCollect.read_utterances_single_dir(stt, directory)
    print('utterances', utterances)

    for key in utterances:
        expected = key.split('_')[0]

        print('bassts?', skill_test(utterances[key], expected, language))


if __name__ == "__main__":
    # wav_eval('mycroft_en', 'test_audio/skill_test/en-us/extern_mic', 'en-us')
    # skill_file = "test_skills/de_skills"

    # skill_lines = [line.rstrip('\n') for line in codecs.open(skill_file, 'r', 'utf-8')]

    # for line in skill_lines:
    #    skill_test(line.split('|')[1].upper(), line.split('|')[0], 'de-de')

    envoked_skill('hello jonas and christoph', 'en-us')

    print('success')
