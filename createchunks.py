import subprocess
import json
from pathlib import Path
import os

#NOTE: diaries_dir and audio_dir should match. i.e., if you have a file called 'myinterview.wav' in your audio_dir, you need a corresponding file called 'myinterview.json' in your diaries_dir
diaries_dir = 'path to dir containing outputs of diarize.py'
audio_dir = "path to dir containing wav files we want to split up"
out_path = "where to save outputted clips"

sen_time = 1.1 #amount of silence that the algorithm assumes is the end of a sentence
max_len = 13.0 #maximum allowed length of one clip of audio

#NOTE: for each source audio file, you need to manually check which speaker ID pyannote assigned your target speaker. Look at the diarization files and listen to the audio.  
desired_speaker = {
        'exampleinterview1.json': 'SPEAKER_01',
        'exampleebook2.json': 'SPEAKER_03',
        'examplespeech3.json': 'SPEAKER_07'
        }

def remove_overlap_check(diary_name, timestamps):
    for i in range(len(timestamps)-1):
        if timestamps[i]['stop'] > timestamps[i+1]['start']:
            print('remove_overlap function failed to remove overlapping audios')
            assert False

#removes some overlapping speaker audio/interruptions/laughter etc. 
def remove_overlap(diary_name, stamps):
    goodies = []
    i = 0
    while i < (len(stamps)-1):
        if stamps[i]['stop'] > stamps[i+1]['start']:
            #print('found a segment with overlap')
            current_end = stamps[i]['stop']
            i += 1
            while (i < len(stamps)) and (current_end > stamps[i]['start']):
                i += 1
        else:
            goodies.append(stamps[i])
            i += 1
    print(f'amount of timestamps in original was {len(stamps)} and after removing timestamps that contained speaker overlap we will keep {len(goodies)}') 
    return goodies


#uses ffmpeg to split source audio into shorter clips
def split_audio(bundled_timestamps, filename, padding=0.1):
    suffix_base = '00000'

    for i, timestamp in enumerate(bundled_timestamps):

        print(timestamp)
        start_time = timestamp["start"] - padding
        stop_time = timestamp["stop"] + padding
        speaker = timestamp['speaker']
        #make the index with leading 0s so that files are nicely in order in dir/metadata.csv
        suffix_string = str(i)
        suffix_start = suffix_base[len(suffix_string):]
        suffix = suffix_start + suffix_string
        output_file = out_path + f"{filename.split('.')[0]}_{speaker}_segment_{suffix}.wav"#f"{filename.split('.')[0]}{filename}Speaker{speaker}output_segment_{i}.wav"
        input_file = audio_dir + filename.split('.')[0] + '.wav'
        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-ss", str(start_time),
            "-to", str(stop_time),
            "-c", "copy",
            output_file
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"An error occurred: {e}")


#algorithm that gathers together chunks of speech from our speaker with max length in seconds max_len. 
def chunk_speech(stamps, desired):
    chunks = []
    current = []
    #gather up all segments at the start from other speakers
    i = 0
    while stamps[i]['speaker'] != desired:
        i += 1
    #set us up on the first segment from our speaker
    current.append(stamps[i])
    start = stamps[i]['start']
    i += 1
    while i < len(stamps):
        assert len(current) > 0
        #we found a segment with our desired speaker and adding it wouldn't exceed our limit
        if stamps[i]['stop'] - start < max_len and stamps[i]['speaker'] == desired:
            #if we appear to be at a natural sentence boundary, pinch it off
            if stamps[i]['start'] - current[-1]['stop'] > sen_time:
                chunks.append(current)
                current = [stamps[i]]
                start = stamps[i]['start']
                i += 1
            #we found a good one and it's not breaking a natural boundary
            else:
                current.append(stamps[i])
                i += 1
        #we found a segment with our desired speaker, but adding it would exceed our limit
        elif stamps[i]['speaker'] == desired:
            chunks.append(current)
            current = [stamps[i]]
            start = stamps[i]['start']
            i += 1
        #we encountered a segment from a different speaker, pinch off existing chunk and clear all of these out of the way
        elif stamps[i]['speaker'] != desired:
            chunks.append(current)
            #clear them all
            while i < len(stamps) and stamps[i]['speaker'] != desired:
                i += 1
            #set current up to contain one of desired
            if (i < len(stamps) - 1):
                current = [stamps[i]]
                start = stamps[i]['start']
                i += 1
            
    return chunks



for diary in os.listdir(diaries_dir) :
    if diary.split('.')[-1] == 'json':
        with open(os.path.join(diaries_dir, diary), 'r') as file:
            print(f'splitting file: {file}')
            timestamps = json.load(file)
            timestamps = remove_overlap(diary, timestamps)
            remove_overlap_check(diary,timestamps)
            chunks = chunk_speech(timestamps, desired_speaker[diary])
            #turn list of lists of dict into list of dicts
            chunks = [{'start':each[0]['start'], 'stop':each[-1]['stop'], 'speaker':each[0]['speaker']} for each in chunks]
            print(f'amount of chunks: {len(chunks)}')
            split_audio(chunks, diary)
            

        
