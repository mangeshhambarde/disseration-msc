#!/usr/bin/env python3

import argparse
import glob
import os
import statistics
import matplotlib.pyplot as plt

"""
Prints statistics about the DIHARD dev/eval datasets.
Currently shown:
    1. Percentage of speech.
    2. Avg length of recordings.
    3. Avg number of speakers per recording.
    4. Avg RTTM segment length.
    5. 

    Usage:
    ./dataset_stats.py <dataset_dir>

    Hierarchy should be like... dataset_dir/data/single_channel...
"""

def rec_id_to_name(rec_id):
    return "DH_{:04d}".format(rec_id)

def rec_name_to_id(rec_name):
    return int(rec_name[3:])

def get_recording_durations(uem_file):
    rec_durations = {}
    rec_id = 1
    with open(uem_file) as f:
        for line in f:
            rec_durations[rec_id] = float(line.split()[-1])
            rec_id += 1
    return rec_durations

def get_percentage_speech(uem_file, sad_dir):
    rec_durations = get_recording_durations(uem_file)

    # calculate percentages.
    rec_percentages = {}
    for rec_id in rec_durations:
        speech_duration = 0.
        sad_file = os.path.join(sad_dir, rec_id_to_name(rec_id)+".lab")
        with open(sad_file) as f:
            for line in f:
                cols = line.split()
                speech_duration += float(cols[1]) - float(cols[0])
        rec_percentages[rec_id] = speech_duration / rec_durations[rec_id] * 100

    return rec_percentages

def get_avg_speaker_turn_length(uem_file, rttm_dir):
    rec_ids = get_recording_durations(uem_file)

def get_num_speakers(rttm_dir):
    speaker_count = {}
    for rttm_file in sorted(glob.glob(rttm_dir + "/DH*rttm")):
        speakers = set()
        with open(rttm_file) as f:
            for line in f:
                speakers.add(line.split()[7])
        basename = os.path.basename(rttm_file)
        rec_name = os.path.splitext(basename)[0]
        speaker_count[rec_name_to_id(rec_name)] = len(speakers)
    return speaker_count

def print_all(flac_dir, rttm_dir, sad_dir, uem_file):
    # Percentage speech.
    rec_percentages = get_percentage_speech(uem_file, sad_dir)
    plt.plot(rec_percentages.keys(), rec_percentages.values())
    plt.xlabel("Recording ID")
    plt.ylabel("% speech")
    plt.savefig("percentage_speech.png")

    # Length of recordings.
    rec_durations = get_recording_durations(uem_file)
    plt.clf()
    plt.plot(rec_durations.keys(), rec_durations.values())
    plt.xlabel("Recording ID")
    plt.ylabel("Length of recording (sec)")
    plt.savefig("recording_lengths.png")

    # Number of speakers.
    speaker_count = get_num_speakers(rttm_dir)
    plt.clf()
    plt.plot(speaker_count.keys(), speaker_count.values())
    plt.xlabel("Recording ID")
    plt.ylabel("Number of speakers")
    plt.savefig("num_speakers.png")
    print("Average number of speakers = ", statistics.mean(speaker_count.values()))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_dir')
    args = vars(parser.parse_args())

    flac_dir = os.path.join(args["dataset_dir"], "data/single_channel/flac")
    rttm_dir = os.path.join(args["dataset_dir"], "data/single_channel/rttm")
    sad_dir = os.path.join(args["dataset_dir"], "data/single_channel/sad")
    uem_file = os.path.join(args["dataset_dir"], "data/single_channel/uem/all.uem")

    print_all(flac_dir, rttm_dir, sad_dir, uem_file)
