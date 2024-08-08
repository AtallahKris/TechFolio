import os
import torch
from transformers import pipeline

# Initialize the speech-to-text pipeline from Hugging Face Transformers
# This uses the "openai/whisper-tiny.en" model for automatic speech recognition (ASR)
# The `chunk_length_s` parameter specifies the chunk length in seconds for processing
asr_pipeline = pipeline(
  "automatic-speech-recognition",
  model="openai/whisper-tiny.en",
  chunk_length_s=30,
)

# Prompt the user to input the path to the audio file
audio_path = input("Enter the path to the audio file: ")

# If the input is just the file name, assume it's in the same directory as the script
if not os.path.isabs(audio_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, audio_path)

# Perform speech recognition on the audio file
# The `batch_size=8` parameter indicates how many chunks are processed at a time
# The result is stored in `transcribed_text` with the key "text" containing the transcribed text
transcribed_text = asr_pipeline(audio_path, batch_size=8)["text"]

# Print the transcribed text to the console
print(transcribed_text)
