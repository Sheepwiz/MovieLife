from pathlib import Path
from openai import OpenAI
import requests
import os
import cv2
import base64
import time
import pygame

# OpenAI API key
client = OpenAI()

# OpenAI API Key
api_key = os.environ.get("OPENAI_API_KEY")
# Path to your image
image_path = "vision.jpg"

# Getting the base64 string
base64_image = "error"

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What’s in this image, describe it in a short one sentence"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 300
}



# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def generate_response(prompt):
    name = "ENTER NAME HERE"
    age = "ENTER AGE HERE"
    location = "ENTER LOCATION HERE"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You're a narrator in a movie for a person named " + name + ". He/She is " + age + " years old an lives in " + location + ". When you get a descript of a scene you continue the narrative from the perspective as " + name + ". Everyone should be in 3rd person"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
      model="tts-1",
      voice="alloy",
      input=text
    )

    response.stream_to_file(speech_file_path)
    return speech_file_path


def capture_webcam_photo(save_directory="webcam_photos"):
    # Create directory if it doesn't exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Open default camera (usually the first camera)
    cap = cv2.VideoCapture(1)

    # Capture frame-by-frame
    ret, frame = cap.read()

    # Generate a unique filename
    filename = os.path.join(save_directory, "webcam_photo.jpg")

    # Save the captured frame as an image
    cv2.imwrite(filename, frame)

    # Release the capture
    cap.release()

    return filename


def play_mp3(file_path):
    # Initialize Pygame
    pygame.init()

    try:
        # Initialize the mixer
        pygame.mixer.init()

        # Load the MP3 file
        pygame.mixer.music.load(file_path)

        # Play the MP3 file
        pygame.mixer.music.play()

        # Wait until the music finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Adjust the playback speed
    except pygame.error as e:
        print(f"Error playing MP3: {e}")
    finally:
        # Cleanup Pygame
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()

while True:
    start_time = time.time()
    saved_path = capture_webcam_photo()
    base64_image = encode_image(saved_path)
    payload["messages"][0]["content"][1]["image_url"]["url"] = "data:image/jpeg;base64," + base64_image
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    jsonZ = response.json()
    response_text = generate_response(jsonZ["choices"][0]["message"]["content"])
    output_file = text_to_speech(response_text)
    play_mp3(output_file)
    # Calculate the time elapsed since the function started
    elapsed_time = time.time() - start_time

    # Wait for the remaining time until 20 seconds have passed
    remaining_time = max(0, 20 - int(elapsed_time))
    time.sleep(remaining_time)
