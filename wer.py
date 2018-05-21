import editdistance


def wer(s1, s2):
    s1 = s1.split()
    s2 = s2.split()
    words = list(set([w for w in s1 + s2]))
    s1 = [words.index(w) for w in s1]
    s2 = [words.index(w) for w in s2]
    return editdistance.eval(s1, s2) * 1.0 / max(len(s1), len(s2))


if __name__ == "__main__":
    print (wer("hallo ich bin", "hallo du bist"))
    print (wer("hallo was geht", "hallo was geht"))