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

def get_rec_ids(uem_file):
    return range(1, len(open(uem_file).readlines())+1)

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

def get_num_speakers(uem_file, rttm_dir):
    speaker_count = {}
    for rec_id in get_rec_ids(uem_file):
        rttm_path = os.path.join(rttm_dir, rec_id_to_name(rec_id)+".rttm")
        speakers = set()
        with open(rttm_path) as f:
            for line in f:
                speakers.add(line.split()[7])
        speaker_count[rec_id] = len(speakers)
    return speaker_count

def get_avg_speaker_turn_length(rttm_dir, uem_file):
    rec_avg_turn_lengths = dict()

    for rec_id in get_rec_ids(uem_file):
        rttm_path = os.path.join(rttm_dir, rec_id_to_name(rec_id)+".rttm")
        turn_lengths = []
        last_speaker = None
        with open(rttm_path) as f:
            for line in f:
                segment_length = float(line.split()[4])
                speaker = line.split()[7]
                if last_speaker is None or speaker != last_speaker: # speaker change happened.
                    turn_lengths.append(segment_length)
                    last_speaker = speaker
                else:
                    turn_lengths[-1] += segment_length # same speaker continued speaking.
        rec_avg_turn_lengths[rec_id] = statistics.mean(turn_lengths)
    return rec_avg_turn_lengths

def do_all(flac_dir, rttm_dir, sad_dir, uem_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    outfile = open(os.path.join(output_dir, "report.txt"), 'w')

    # Percentage speech.
    rec_percentages = get_percentage_speech(uem_file, sad_dir)
    plt.plot(rec_percentages.keys(), rec_percentages.values())
    plt.xlabel("Recording ID")
    plt.ylabel("% speech")
    plt.savefig(os.path.join(output_dir, "percentage_speech.png"))

    # Length of recordings.
    rec_durations = get_recording_durations(uem_file)
    plt.clf()
    plt.plot(rec_durations.keys(), rec_durations.values())
    plt.xlabel("Recording ID")
    plt.ylabel("Length of recording (sec)")
    plt.savefig(os.path.join(output_dir, "recording_lengths.png"))

    # Number of speakers.
    speaker_count = get_num_speakers(uem_file, rttm_dir)
    for rec_id in speaker_count:
        print("Num speakers", rec_id_to_name(rec_id), speaker_count[rec_id], file=outfile)
    plt.clf()
    plt.plot(speaker_count.keys(), speaker_count.values())
    plt.xlabel("Recording ID")
    plt.ylabel("Number of speakers")
    plt.savefig(os.path.join(output_dir, "num_speakers.png"))
    print("Average number of speakers = ", statistics.mean(speaker_count.values()), file=outfile)

    # Avg speaker turn length.
    avg_turn_length = get_avg_speaker_turn_length(rttm_dir, uem_file)
    for rec_id in avg_turn_length:
        print("Avg turn length", rec_id_to_name(rec_id), avg_turn_length[rec_id], file=outfile)
    plt.clf()
    plt.plot(avg_turn_length.keys(), avg_turn_length.values())
    plt.xlabel("Recording ID")
    plt.ylabel("Avg turn length")
    plt.savefig(os.path.join(output_dir, "avg_turn_length.png"))

    outfile.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_dir')
    parser.add_argument('output_dir')
    args = vars(parser.parse_args())

    flac_dir = os.path.join(args["dataset_dir"], "data/single_channel/flac")
    rttm_dir = os.path.join(args["dataset_dir"], "data/single_channel/rttm")
    sad_dir = os.path.join(args["dataset_dir"], "data/single_channel/sad")
    uem_file = os.path.join(args["dataset_dir"], "data/single_channel/uem/all.uem")
    output_dir = args["output_dir"]

    do_all(flac_dir, rttm_dir, sad_dir, uem_file, output_dir)
