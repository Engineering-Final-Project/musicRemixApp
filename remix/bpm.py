import array
import math
import wave

import numpy
import pywt
from scipy import signal


def read_wav(filename):
    """
    A function to read a wav file
    :param filename: the name of the file
    :return: the number of samples and the sampling frequency of the audio
    """
    # open file, get metadata for audio
    wf = wave.open(filename, "rb")

    nsamps = wf.getnframes()
    assert nsamps > 0

    fs = wf.getframerate()
    assert fs > 0

    # Read entire file and make into an array
    samps = list(array.array("i", wf.readframes(nsamps)))

    assert nsamps == len(samps)
    return samps, fs


def no_audio_data():
    """
    prints an error when no data can be found
    :return: None
    """
    raise Exception("No audio data for sample, skipping...")


def peak_detect(data):
    """
    A simple peak detection
    :param data: the audio to detect
    :return: the peak
    """
    max_val = numpy.amax(abs(data))
    peak_ndx = numpy.where(data == max_val)
    if len(peak_ndx[0]) == 0:  # if nothing found then the max must be negative
        peak_ndx = numpy.where(data == -max_val)
    return peak_ndx


def bpm_detector_helper(data, fs):
    """
    A function to apply the Discrete Wavelet Transform to an audio, filter it, calculate its auto-correlation and bpm
    :param data: the input data
    :param fs: the sampling frequency of the data
    :return: bpm, correlation
    """
    cA = []
    cD_sum = []
    levels = 4
    max_decimation = 2 ** (levels - 1)
    min_ndx = math.floor(60.0 / 220 * (fs / max_decimation))
    max_ndx = math.floor(60.0 / 40 * (fs / max_decimation))

    for loop in range(0, levels):
        # 1) DWT
        if loop == 0:
            [cA, cD] = pywt.dwt(data, "db4")
            cD_minlen = len(cD) / max_decimation + 1
            cD_sum = numpy.zeros(math.floor(cD_minlen))
        else:
            [cA, cD] = pywt.dwt(cA, "db4")

        # 2) Filter
        cD = signal.lfilter([0.01], [1 - 0.99], cD)

        # 4) Subtract out the mean.

        # 5) Decimate for reconstruction later.
        cD = abs(cD[:: (2 ** (levels - loop - 1))])
        cD = cD - numpy.mean(cD)

        # 6) Recombine the signal before ACF
        # Essentially, each level the detail coefs (i.e. the HPF values) are concatenated to the beginning of the array
        cD_sum = cD[0 : math.floor(cD_minlen)] + cD_sum

    if not [b for b in cA if b != 0.0]:
        return no_audio_data()

    # Adding in the approximate data as well...
    cA = signal.lfilter([0.01], [1 - 0.99], cA)
    cA = abs(cA)
    cA = cA - numpy.mean(cA)
    cD_sum = cA[0 : math.floor(cD_minlen)] + cD_sum

    # ACF
    correl = numpy.correlate(cD_sum, cD_sum, "full")

    midpoint = math.floor(len(correl) / 2)
    correl_midpoint_tmp = correl[midpoint:]
    peak_ndx = peak_detect(correl_midpoint_tmp[min_ndx:max_ndx])
    if len(peak_ndx) > 1:
        return no_audio_data()

    peak_ndx_adjusted = peak_ndx[0] + min_ndx
    bpm = 60.0 / peak_ndx_adjusted * (fs / max_decimation)
    # print(bpm)
    return bpm, correl


def bpm_detector(filename, window=10):
    """
    A function to detect the bpm of an audio
    :param filename: the path to the audio file
    :param window: the number of samples in each window
    :return: the bpm, correlation
    """
    global correl, bpm, n
    samps, fs = read_wav(filename)
    correl = []
    bpm = 0
    n = 0
    nsamps = len(samps)
    window_samps = int(window * fs)
    samps_ndx = 0  # First sample in window_ndx
    max_window_ndx = math.floor(nsamps / window_samps)
    bpms = numpy.zeros(max_window_ndx)
    # Iterate through all windows
    for window_ndx in range(0, max_window_ndx):

        # Get a new set of samples
        data = samps[samps_ndx: samps_ndx + window_samps]
        if not ((len(data) % window_samps) == 0):
            raise AssertionError(str(len(data)))

        bpm, correl_temp = bpm_detector_helper(data, fs)
        if bpm is None:
            continue
        bpms[window_ndx] = bpm
        correl = correl_temp

        # Iterate at the end of the loop
        samps_ndx = samps_ndx + window_samps

        # Counter for debug...
        n = n + 1
    return_value = numpy.median(bpms)
    if return_value > 180:
        return_value *= 0.5
    if return_value < 60:
        return_value *= 2
    return return_value, correl
