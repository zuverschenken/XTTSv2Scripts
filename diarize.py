import torchaudio
import torch
import json
import os
from pyannote.audio import Pipeline

my_token = 'put your access token here!'#https://github.com/pyannote/pyannote-audio

in_files = 'path to at least one .wav file with some speech in it'
outdir = 'path to output diary files to'

#load pipeline and move to gpu
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=my_token)

pipeline.to(torch.device('cuda'))

#diarize each file in turn
for file in os.listdir(in_files):
    print(f"diarizing {file}...")
    file_path = in_files + file
    waveform, sample_rate = torchaudio.load(file_path)
    audio = {"waveform": waveform, "sample_rate": sample_rate}
    diarization = pipeline(audio)
    write = [{'start': turn.start, 'stop': turn.end, 'speaker': speaker} for turn, _, speaker in diarization.itertracks(yield_label=True)]
    #write the diarization to json
    unique = file.split('.')[0]
    outpath = outdir + unique + '.json'
    with open(outpath, 'w') as json_file:
        json.dump(write, json_file, indent=2)
