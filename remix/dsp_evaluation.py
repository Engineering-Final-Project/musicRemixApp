import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import wave

from remix.audio import *
from remix.tools import Tools


def plot_image(path):
    """
    Plot an image from a path
    :param path: the path of the image
    :return: None
    """
    img = mpimg.imread(path)
    plt.imshow(img)
    plt.show()


def get_np_array(sound: AudioSegment):
    """
    A function to get the NumPy array representation of an audio file
    :param sound: an AudioSegment object
    :return: the numpy array representing sound
    """
    samples = sound.get_array_of_samples()
    arr = np.array(samples)  # arr.size: 17094656
    return arr


def get_wave_data(wav_file):
    """
    A function to obtain sampling frequency, time space and channels of an audio file
    :param wav_file: a wav file
    :return: sampling frequency, time space, channels
    """
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
    """
    A function to plot the waveform of an audio file
    :param wav: a wav audio file
    :return: None
    """
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
    """
    A function to plot the beats of an audio on its waveform
    :param wav: the wav file to plot
    :param bpm: the bpm of the wav file (bpm = 1/ beats per minute)
    :return: None
    """
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
    """
    A function to plot the onset times on the waveform of an audio
    :param wav: the wav file to plot
    :param onset: the onset times of wav
    :return: None
    """
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
