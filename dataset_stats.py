#!/usr/bin/env python3

import argparse
import os
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

def percentage_speech(uem_file, sad_dir):
    rec_percentages = {}

    # calculate durations.
    rec_durations = {}
    with open(uem_file) as f:
        for line in f:
            rec_id = line.split()[0]
            rec_durations[rec_id] = float(line.split()[-1])

    # calculate percentages.
    for rec_id in rec_durations:
        speech_duration = 0.
        sad_file = os.path.join(sad_dir, rec_id+".lab")
        with open(sad_file) as f:
            for line in f:
                cols = line.split()
                speech_duration += float(cols[1]) - float(cols[0])
        rec_percentages[rec_id] = speech_duration / rec_durations[rec_id] * 100

    return rec_percentages

def print_all(flac_dir, rttm_dir, sad_dir, uem_file):
    rec_percentages = percentage_speech(uem_file, sad_dir)

    for rec_id, per in rec_percentages.items():
        print(rec_id, per)

    plt.plot(range(1,len(rec_percentages)+1), rec_percentages.values())
    plt.xlabel("Recording ID")
    plt.ylabel("% speech")
    plt.savefig("percentage_speech.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_dir')
    args = vars(parser.parse_args())

    flac_dir = os.path.join(args["dataset_dir"], "data/single_channel/flac")
    rttm_dir = os.path.join(args["dataset_dir"], "data/single_channel/rttm")
    sad_dir = os.path.join(args["dataset_dir"], "data/single_channel/sad")
    uem_file = os.path.join(args["dataset_dir"], "data/single_channel/uem/all.uem")

    print_all(flac_dir, rttm_dir, sad_dir, uem_file)
