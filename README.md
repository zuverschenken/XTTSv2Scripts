Collection of helper scripts for creating LJSpeech format dataset for TTS. [here](https://www.kaggle.com/code/maxbr0wn/tutorial-fine-tuning-xttsv2-english/) is the main notebook referencing this.

I'm assuming you're starting with 1 or more long WAV audio files that all contain at least some speech from your target speaker and you want to turn it into a LJSpeech style dataset.

1. Give your source audio to diarize.py to create diarization files
2. Give the diarization files and your source audio files to createchunks.py to create short clips of speech
3. Give your short clips of speech to transcribeaudio.py to create the text transcription you will use for training
