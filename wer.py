import editdistance
import evaluationSTT

prompts = 'test_audio/skill_wer_test/de-de/extern_mic/etc/PROMPTS'


def wer(s1, s2):
    s1 = s1.split()
    s2 = s2.split()
    words = list(set([w for w in s1 + s2]))
    s1 = [words.index(w) for w in s1]
    s2 = [words.index(w) for w in s2]
    return editdistance.eval(s1, s2) * 1.0 / max(len(s1), len(s2))


def sentence_error_rate(dic1, dic2):
    correct = 0
    total = 0

    for key in dic1:
        total += 1
        if editdistance.eval(dic1[key], dic2[key]) == 0:
            correct += 1
    return 1 - (correct * 1.0 / total)


def total_wer(dic1, dic2):
    string1 = ''
    string2 = ''

    for key in dic1:
        string1 += ' ' + dic1[key]
        string2 += ' ' + dic2[key]

    return wer(string1, string2)


if __name__ == "__main__":
    print(wer('hallo ich es wie ist das wetter', 'hallo ich bin es wie ist das wetter'))

# transcription_dic = evaluationSTT.create_transcriptions_from_file(english_prompts)


