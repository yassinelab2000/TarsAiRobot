'''
This file is responsible for transcribing audio from your microphone into text. which will later be sent to ChatGPT.
You can run it separately for testing purposes !!

Note:
- The PyAudio library gives your code access to your microphone input and output. We are using Vosk with this module to transcribe audio to text.

You will need to download the folder vosk-model-small-en-us-0.15 from https://alphacephei.com/vosk/models (path to the folder here in our code is : model = Model("vosk-model-small-en-us-0.15"))
Install the required packages using : pip install vosk pyaudio

Copyright (c) 2025 Yassine Labiade
Licensed under the MIT License.
'''

from vosk import Model, KaldiRecognizer
import pyaudio
import json
import time

model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

current_partial = ""
is_listening = False

def transcribe_once_from_mic(timeout=2): # timeout = 2 is how many seconds of silence are required to stop transcribing.
    global current_partial, is_listening

    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=16000,
                     input=True,
                     frames_per_buffer=4000)
    stream.start_stream()

    print("Microphone resumed")
    is_listening = True
    current_partial = ""
    last_speech_time = time.time()
    final_text = ""

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False) # data: raw audio that is being recorded in real time.

            if recognizer.AcceptWaveform(data):                   # AcceptWaveform returns True if silence was detected.
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    print(f"Recognized: {text}")
                    final_text += text + " "
                    last_speech_time = time.time()  # updates time
            else:
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "")
                current_partial = partial_text
                if partial_text:
                    print(f"Partial: {partial_text}", end="\r")
                    last_speech_time = time.time()

            # Stop if user is silent for given timeout
            if time.time() - last_speech_time > timeout:
                print("\nSilence detected. Stopping.")
                break

    finally:
        stream.stop_stream() #stops the recording
        stream.close()       #closes the connection
        pa.terminate()       #shuts down the audio system
        is_listening = False
        print("Microphone paused")

    return final_text.strip()

def get_current_partial():
    return current_partial

def is_currently_listening():
    return is_listening

# In case you want to test this module, run this file separately.
if __name__ == "__main__":
    print("Testing mic input...")
    print(transcribe_once_from_mic())
