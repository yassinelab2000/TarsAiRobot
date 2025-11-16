'''
# GPT Module
This Module is the "AI Brain" of your assistant! 
It handles all intelligent conversations,
memory, weather queries, time/date questions, 
and even image analysis.

# IMPORTANT SETUP INSTRUCTIONS:

BEFORE RUNNING THIS MODULE:

1. OPENAI API SETUP:
   - Create account at: https://platform.openai.com
   - Go to Dashboard → API Keys → Create new secret key
   - Copy your key and paste in: client = OpenAI(api_key="YOUR_ACTUAL_KEY_HERE")
     Keep the double quotes - the key must be a string!

2. OPENAI BILLING:
   - Go to Dashboard → Billing → Add to credit balance
   - Add ~$5 credit (enough for testing)

3. WEATHER API SETUP:
   - Create account at: https://openweathermap.org
   - Go to Dashboard → My API Keys → Copy your key
   - Paste in: WEATHER_API_KEY = "YOUR_ACTUAL_WEATHER_KEY_HERE"
   - Also set your city: WEATHER_LOCATION = "YOUR_CITY_NAME_HERE"
   - Make sure city spelling matches OpenWeatherMap's database

4. OPTIONAL PERSONALIZATION:
   - You can modify the SYSTEM_PROMPT to customize TARS's personality
   - Change the name, location, or personality traits as desired

Note: Keep your API keys secret! 

Copyright (c) 2025 Yassine Labiade
Licensed under the MIT License.

'''
from openai import OpenAI #pip install openai
import json
import os
import base64
import requests #pip install requests
from datetime import datetime

# Global variables and constants 
client = OpenAI(api_key="Your_Key")

MEMORY_FILE = "tars_memory.json"
WEATHER_API_KEY = "Your_Key"
WEATHER_LOCATION = "Your_City"

SYSTEM_PROMPT = (
    "You are TARS, an assistant robot created by Yassine Labiade in Hamburg Germany, using the voice of Bill Irwin."
    "You respond concisely, warmly, and with a touch of dry humor. "
    "You can adjust your humor and human-likeness if asked."
)

# Memory System - The Remembering Part 

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory[-8:], f, indent=4)


# Weather Functionality

def get_weather_report():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={WEATHER_LOCATION}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()


        if response.status_code != 200 or "main" not in data:
            return "Sorry, I couldn't retrieve the weather right now."


        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]


        return (f"The weather in {WEATHER_LOCATION} is currently {weather_desc} with a temperature of {temp}°C, "
                f"feels like {feels_like}°C, humidity at {humidity}%, and wind speed of {wind_speed} m/s.")


    except Exception as e:
        return "I ran into an error while checking the weather."
    

# Main AI Function - The Thinking Part 

def generate_tars_reply(user_input):
    # Time and Weather Handling 
    if "time" in user_input:
        now = datetime.now().strftime("%H:%M")
        return f"The current time is {now}."


    if "date" in user_input:
        today = datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}."


    if "weather" in user_input or "temperature" in user_input:
        return get_weather_report()


    #  Memory + ChatGPT logic
    # Prepare Conversation History

    memory = load_memory()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for exchange in memory[-8:]:
        messages.append({"role": "user", "content": exchange["user"]})
        messages.append({"role": "assistant", "content": exchange["tars"]})
    messages.append({"role": "user", "content": user_input})

    # Choose AI Model
    model_to_use = "gpt-3.5-turbo"
    if "think deeply" in user_input.lower() or "analyze deeply" in user_input.lower():
        model_to_use = "gpt-4o"

    # Get AI Response
    response = client.chat.completions.create(
        model=model_to_use,
        messages=messages
    )


    tars_reply = response.choices[0].message.content.strip()
    memory.append({"user": user_input, "tars": tars_reply})
    save_memory(memory)
    return tars_reply


# Vision support ( Image File → Binary Data → Base64 Text → ChatGPT )

def analyze_image(image_path):
    with open(image_path, "rb") as f:
        img_bytes = f.read()


    base64_img = base64.b64encode(img_bytes).decode("utf-8")


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are TARS, a visual AI assistant. Analyze the user's image and describe what you see."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_img}"
                        }
                    }
                ]
            }
        ]
    )


    return response.choices[0].message.content.strip()



