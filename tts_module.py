"""
This module is responsible for splitting text into sentences and converting each sentence
into TARS's voice using the ElevenLabs Text-to-Speech API.

You can test this module independently by running it separately.
However, note that it cannot be used independently or as part of the main application
without following the setup instructions below.

──────────────────────────────
Setup Instructions:
──────────────────────────────
1. Install FFMPEG
   - FFMPEG is required to play and manipulate audio files.
   - Download it from: https://ffmpeg.org/download.html

2. Create an ElevenLabs Account
   - Sign up at: https://elevenlabs.io
   - Create a voice trained on Bill Irwin (the voice actor for TARS from *Interstellar*).
   - You can find sample audio in this repository to help train the model on Bill's voice.

3. Set up your custom voice
   - After training, go to the ElevenLabs sidebar → **Voices** → **My Voices**.
   - Select your trained voice and copy its **Voice ID**.
   - Replace the placeholder value in this module:
       VOICE_ID = "Tars_Voice_ID"
     with your actual Voice ID as a string.

4. Get your ElevenLabs API Key
   - Go to the sidebar → **Developers** → **API Keys**.
   - Create a new key, copy it, and ensure the "Text to Speech" permission is enabled.
   - Replace the placeholder value in this module:
       API_KEY = "Your_Key"
     with your actual API key as a string.

5. Install Required Python Packages (for standalone testing)
   - Run: pip install requests

──────────────────────────────
Once these steps are completed, you can run this module independently

Copyright (c) 2025 Yassine Labiade
Licensed under the MIT License.
"""

import requests
import tempfile
import subprocess
import os
import re


API_KEY = "Your_Key"
VOICE_ID = "Tars_Voice_ID"


def speak(text):
    print(f"TARS is speaking: {text}")
    sentences = split_into_sentences(text)
    temp_files = []


    for sentence in sentences:
        if not sentence.strip():
            continue


        audio_path = generate_tts_chunk(sentence)
        if audio_path:
            temp_files.append(audio_path)


    for path in temp_files:
        subprocess.run([
            "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path
        ])
        os.remove(path)


def generate_tts_chunk(sentence):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    data = {
        "text": sentence,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.8
        }
    }


    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(response.content)
            return temp_audio.name
    else:
        print(f"Error from ElevenLabs: {response.status_code} - {response.text}")
        return None


def split_into_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text.strip())


if __name__ == "__main__":
    speak("Hey, I am the upgraded TARS. I speak smarter, smoother, and I don’t crash anymore.")
