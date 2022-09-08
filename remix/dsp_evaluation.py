import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import wave

from remix.audio import *
from remix.tools import Tools


def plot_image(path):
    """
    Plot an image from a path
    """
    img = mpimg.imread(path)
    plt.imshow(img)
    plt.show()


def get_np_array(sound: AudioSegment):
    samples = sound.get_array_of_samples()
    arr = np.array(samples)  # arr.size: 17094656
    return arr


def get_wave_data(wav_file):
    # Extract Raw Audio from Wav File
    signal = wav_file.readframes(-1)  # len=11866112
    signal = np.frombuffer(signal, dtype='int16')

    # Split the data into channels
    channels = [[] for channel in range(wav_file.getnchannels())]
    # len(channels) = 2, type(channels)=<class 'list'>, len(channels[0])=5933056, type(channels[0])=<class 'list'>
    for index, datum in enumerate(signal):
        channels[index % len(channels)].append(datum)

    # Get time from indices
    fs = wav_file.getframerate()
    # type(time)=<class 'numpy.ndarray'>, time.size=5933056, time.dtype=float64
    time = np.linspace(0, len(signal) / len(channels) / fs, num=int(len(signal) / len(channels)))
    return fs, time, channels


def plot_array(wav):
    with wave.open(wav, 'r') as wav_file:
        fs, time, channels = get_wave_data(wav_file)

        # Plot
        plt.figure(1)
        plt.xlabel("Time (secs)")
        plt.title('Signal Waveform with BPM and Onsets')
        for channel in channels:
            plt.plot(time, channel, color='navy')
        plt.savefig("/home/miriams/PycharmProjects/remixProject/tests/tests_try/wav graph")
        plt.show()


def plot_array_bpm(wav, bpm):
    with wave.open(wav, 'r') as wav_file:
        fs, time, channels = get_wave_data(wav_file)

        # Plot
        plt.figure()
        plt.title('Signal Waveform with BPM')
        plt.xlabel("Time (secs)")
        x_len = 0
        for channel in channels:
            if x_len < len(channel):
                x_len = len(channel)
            plt.plot(time, channel, color='navy')
        bps = (1 / (bpm / 60)) # 1.35
        x = 0.04
        audio_secs = x_len / fs
        while x < audio_secs:
            plt.axvline(x=x, color='red', label='axvline - full height')
            x += bps

        plt.savefig("/home/miriams/PycharmProjects/remixProject/tests/tests_try/bpm graph")
        plt.show()


def plot_array_onset(wav, onset):
    with wave.open(wav, 'r') as wav_file:
        fs, time, channels = get_wave_data(wav_file)

        # Plot
        plt.figure()
        plt.title('Signal Waveform with Onsets')
        plt.xlabel("Time (secs)")
        for channel in channels:
            plt.plot(time, channel, color='navy')
        plt.plot(onset, '.', color='yellow')
        plt.savefig("/home/miriams/PycharmProjects/remixProject/tests/tests_try/onset graph")
        plt.show()


if __name__ == "__main__":
    # s = AudioSegment.from_file("/home/miriams/PycharmProjects/remixProject/remix/demo/"
    #                            "Nuvole Bianche (by Ludovico Einaudi) for Two Cellos - Mr & Mrs Cello.mp3")
    # # array = get_np_array(s)
    # wav_path = "/home/miriams/PycharmProjects/remixProject/tests/tests_try/wav_einaudi"
    # s.export(wav_path, format="wav")
    # s_bpm = Tools.bpm_detector(s)  # Queen_median=81.24539425202653, einaudi_median=98.79253567508232
    # plot_array_bpm(wav_path, s_bpm)
    # onsets = Tools.onset(s)  # list of floats of length=308 (Queen)
    # plot_array_onset(wav_path, onsets)

    # queen = AudioSegment.from_file("we_will_rock_you.mp3")
    # wav_path = "we_will_rock_you.wav"
    # queen.export(wav_path, format="wav")
    # queen_bpm = Tools.bpm_detector(queen)  # 81.35558372418976
    # plot_array_bpm(wav_path, queen_bpm/2)
    # onsets = Tools.onset(queen)  # list of floats of length=308 (Queen)
    # plot_array_onset(wav_path, onsets)

    einaudi = AudioSegment.from_file('Ludovico Einaudi - Nuvole Bianche.mp3')
    wav_path = "einaudi.wav"
    einaudi.export(wav_path, format="wav")
    einaudi_bpm = Tools.bpm_detector(einaudi)  # 93.72590358505852
    # print(einaudi_bpm)
    plot_array_bpm(wav_path, einaudi_bpm / 4)

    # young = AudioSegment.from_file("/home/miriams/PycharmProjects/remixProject/remix/demo/Alphaville - Forever Young ~Official Video.mp3")
    # wav_path = "young.wav"
    # young.export(wav_path, format="wav")
    # bpm = Tools.bpm_detector(young)  # 69.07137375287797
    # print(bpm)
    # plot_array_bpm(wav_path, bpm)
