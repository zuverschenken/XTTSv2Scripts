import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
import os
import csv

audio_path = 'path to audio clips created by createchunks.py'
csv_path = 'output csv file from this transcription process'
file_names = os.listdir(audio_path)
#create transcripts for audio files

#set up and init model 
print("setting up model...")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id, language='en') 

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=32, 
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)

print("performing speech recognition...")
#transcribe each clip and store its text

#TODO: This should be done in batches with dataset. Not a big deal if you're just doing this once.
file_names = os.listdir(audio_path)
lines = []
for name in file_names:
    audio = audio_path+name
    result = pipe(audio)["text"]
    #store in LJ speech format (filename, transcript, normalised transcript)
    lines.append((name.split('.')[0], result, result))

with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter='|')
    for row in lines:
        csv_writer.writerow(row)

print("written to csv")
