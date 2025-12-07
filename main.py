"""
This module serves as the control center that coordinates and manages all other modules
within the TARS system.

Important Notes !!!

Before running this program:
1. Ensure that all other TARS modules are already set up and that you have followed
   the setup instructions written at the top of each module.

2. Create an account on https://picovoice.ai to obtain your Access Key.
   - Assign your access key to the variable:
       access_key = "Your_access_Key"
     (Replace the placeholder with your actual key.)

3. Download your .ppn wake-word file trained on the phrase "Hey TARS":
   - Use the Raspberry Pi version if you are running this on a Raspberry Pi.
   - Use the Windows version if you are running this on Windows.
   - Rename the file to "hey_tars.ppn" and place it in the same directory as main.py.

   The .ppn file is a trained AI model that mathematically represents the sound
   pattern of the wake word "Hey TARS".

Controls:
- Press ESC to exit the application.

Copyright (c) 2025 Yassine Labiade
Licensed under the MIT License.
"""


import struct
import pyaudio
import pvporcupine
import os
import pygame
import time
import cv2 # for windows 
import tempfile
import threading


from mic_speech_module import transcribe_once_from_mic, get_current_partial, is_currently_listening
from display_module import run_live_text_black_screen, draw_matrix
from tts_module import speak
from gpt_module import generate_tars_reply, analyze_image


# Wake word setup

access_key = "Your_access_Key"
keyword_path = os.path.join(os.getcwd(), "hey_tars.ppn")


porcupine = pvporcupine.create(
    access_key=access_key,
    keyword_paths=[keyword_path]
)

# Audio Stream Setup (opens microphone for wake word detection)

pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,  # matches wake word detector
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)


# Pygame setup : creates fullscreen Matrix style display.

WIDTH, HEIGHT = 800, 600
FPS = 60
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("TARS Matrix Display")
clock = pygame.time.Clock()

# Cleanup Function (closes audio resources when program exits)

def cleanup_audio():
    audio_stream.close()
    pa.terminate()
    porcupine.delete()



#  Image Capture Function (Raspberry Pi camera)  

def capture_and_save_image():
    #Create Temporary File Path
    temp_path = os.path.join(tempfile.gettempdir(), "tars_view.jpg")
    try:
        # Capture image using rpicam-still / Runs a shell command from Python
        # Takes a still photo / Save to this file / Image width and Height in pixels / Don't show preview window / max wait 1s
        result = os.system(f"rpicam-still -o {temp_path} --width 640 --height 480 --nopreview --timeout 1000")
        # Check if Successful as 0 = success in Unix & File was actually created
        if result == 0 and os.path.exists(temp_path):
            print(f"Picture captured using rpicam-still to {temp_path}")
            return temp_path
        else:
            print("Failed to capture image with rpicam-still.")
            return None
    except Exception as e:
        # Prints the error for debugging
        print(f"Exception while using rpicam-still: {e}")
        return None # if note then none


# Wake Word Detection
# Check if Hey TARS was spoken

def listen_for_wake_word():
    # Clear any buffered audio / Without flushing you hear old audio (delayed)
    audio_stream.read(audio_stream.get_read_available(), exception_on_overflow=False)

    # Read Fresh Audio Chunk (pcm: Raw binary audio data)
    pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
    # Convert binary to numbers
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
    # Check if wake word detected (Does this 32ms sound like 'Hey TARS'?)
    keyword_index = porcupine.process(pcm)
    # -1 = No wake word detected
    #  0 = First wake word detected 
    #  1 = Second wake word detected etc
    return keyword_index >= 0


def main():
    try:
        print("TARS is on. Waiting for wake word")


        while True:
            # Matrix animation always running
            # Two ways to quit
            # Click X button on window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cleanup_audio()
                    pygame.quit()
                    return
                # or ESC key
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        cleanup_audio()
                        pygame.quit()
                        return


            draw_matrix() # Matrix animation )
            pygame.display.flip() #  Updates screen with new frame
            clock.tick(FPS)

            #Listen for "Hey TARS" / Continuously checks if you say it.
            if listen_for_wake_word():
                print("Wake word detected!")


                result_container = [] # Empty list to store transcribed text

                # Start Listening to User /  Listen to microphone + update display
                # Listening to User
                def run_transcription():
                    text = transcribe_once_from_mic(timeout=2) # Listens for 2 seconds of silence
                    result_container.append(text)

                # update display
                transcribe_thread = threading.Thread(target=run_transcription)
                transcribe_thread.start()

                # Show Live Speech Display
                # Switches display from Matrix to black screen
                run_live_text_black_screen(
                    get_live_text=get_current_partial, # Gets real time "what you're saying now"
                    final_text_container=result_container, # Where final text will be stored
                    is_listening_func=is_currently_listening # Checks if microphone is active
                )

                # Wait for listening to finish
                transcribe_thread.join()

                # Process User Request
                if result_container: 
                    user_input = result_container[0].strip().lower()
                    print(f"User said: {user_input}") # what user said for debugging

                    # Handle Vision Command
                    if "what do you see" in user_input or "show me what you see" in user_input:
                        image_path = capture_and_save_image()
                        if image_path:
                            speak("Analyzing the scene. Please wait a moment.")
                            vision_reply = analyze_image(image_path)
                            speak(vision_reply)
                        else:
                            speak("Sorry, I couldn't access the camera.")
                    else:
                        tars_reply = generate_tars_reply(user_input)
                        speak(tars_reply)


                print("Listening for wake word again...")

    except KeyboardInterrupt:
        cleanup_audio() # Closes microphone
        pygame.quit() # quit the app
        print("Exiting")


if __name__ == "__main__":
    main()




