import evaluationSTT
from os.path import join
import os
import numpy as np
import matplotlib
from matplotlib import rcParams

matplotlib.use('pdf')
import matplotlib.pyplot as plt

stt_testlist = ['deepspeech_de', 'mycroft_de', 'deepspeech_en', 'mycroft_en']
colorlist = ['r', 'b', 'g', 'y']

directory = 'test_audio/voxforge'


# reads utterances from directory with standard folders. WAVs are in directory/*/wav
def read_all_utterances(stt, root_dir=directory):
    utterances_dic = {}
    for folder in os.listdir(root_dir):
        utterances_dic.update(evaluationSTT.create_utterances_from_wavfiles(join(root_dir, folder, 'wav'), stt))
    return utterances_dic


def read_utterances_single_dir(stt, root_dir=directory):
    utterances_dic = {}
    utterances_dic.update(evaluationSTT.create_utterances_from_wavfiles(root_dir, stt))
    return utterances_dic


def read_all_transcriptions(root_dir):
    transcription_dic = {}
    for folder in os.listdir(root_dir):
        transcription_dic.update(
            evaluationSTT.create_transcriptions_from_file(join(root_dir, folder, 'etc', 'PROMPTS')))
    return transcription_dic


def plot_stt_evaluation(sttlist, colors):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    major_ticks = np.arange(0, 101, 5)
    minor_ticks = np.arange(0, 101, 1)

    ax.set_yticks(major_ticks)
    ax.set_yticks(minor_ticks, minor=True)
    ax.grid(which='minor', alpha=0.2)

    table_columns = ('character distance', 'wer', 'sentences error rate')
    table_rows = sttlist

    cell_text = []

    for stt, color in zip(sttlist, colors):
        lang = stt.split('_')[1]
        evaluationSTT.wav_readtimes = []
        evaluationSTT.wav_durs = []
        uttdic = read_all_utterances(stt, join(directory, lang))
        transdic = read_all_transcriptions(join(directory, lang))

        fit = np.polyfit(evaluationSTT.wav_durs, evaluationSTT.wav_readtimes, 1)
        fit_fn = np.poly1d(fit)

        x_axis = np.linspace(0, 15, 5)
        y_axis = fit_fn(x_axis)

        plt.plot(evaluationSTT.wav_durs, evaluationSTT.wav_readtimes, color + 'o')
        plt.plot(x_axis, y_axis, '-' + color, label=stt)

        cell_text.append(
            (evaluationSTT.total_edit_distance(uttdic, transdic, stt), evaluationSTT.total_wer(uttdic, transdic),
             evaluationSTT.sentence_error_rate(uttdic, transdic)))

    plt.axis([0, 15, 0, 50])
    plt.xlabel('audio duration in sec')
    plt.ylabel('process time of stt-engine in sec')

    plt.subplots_adjust(top=0.8)

    # leg = plt.legend(loc='lower right', ncol=2, mode="expand", shadow=True, fancybox=True)
    # leg.get_frame().set_alpha(0.5)

    plt.grid('on')

    plt.table(cellText=cell_text, rowLabels=table_rows, rowColours=colors, colLabels=table_columns, loc='top')
    plt.show()
    plt.savefig('test')


if __name__ == "__main__":
    plot_stt_evaluation(stt_testlist, colorlist)

    print('success')
