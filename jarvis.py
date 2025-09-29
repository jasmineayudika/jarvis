from os import system
from gpt4all import GPT4All
import sys
import whisper
import warnings
import time
import webbrowser
import os
import sounddevice as sd
import soundfile as sf

model_path = os.path.expanduser("~/Library/Application Support/nomic.ai/GPT4All/Chocolatine-3B-Instruct-DPO-Revised-Q4_0.gguf")
model = GPT4All(model_path, allow_download=False)
assistant_name = "jarvis"
should_run = True
base_model = whisper.load_model("tiny")

if sys.platform != 'darwin':
    import pyttsx3
    engine = pyttsx3.init() 

askingAQuestion = False

def respond(text):
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say -v Daniel '{clean_text}'")
    else:
        engine.say(text)
        engine.runAndWait()

def listen_for_command():
    samplerate = 16000
    duration = 5

    print("J.A.R.V.I.S. is at your service...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    sf.write("command.wav", recording, samplerate)

    try:
        command = base_model.transcribe("command.wav")
        if command and command['text']:
            print("You said:", command['text'])
            return command['text'].lower()
        return None
    except Exception as e:
        print("Error transcribing audio:", e)
        return None

def perform_command(command):
    global askingAQuestion
    global should_run
    if command:
        print("Command: ", command)
        if "open instagram" in command:
            respond("As you wish.")
            webbrowser.open("https://www.instagram.com/jasmine_ayudika/")
        elif "house party protocol" in command:
            respond("Will do, sir.")
            webbrowser.open("https://youtu.be/sqp0xRN-NxY?si=8y60pJcqH6QqxYcB&t=15")
        elif "ask a question" in command:
            askingAQuestion = True
            respond("What's the question, sir?")
            return
        elif askingAQuestion:
            askingAQuestion = False
            respond("Thinking...")
            print("User command:", command)
            prompt = f"Answer concisely and only about this question: {command}"
            output = model.generate(prompt, max_tokens=200)
            import re
            clean_output = (
                output.replace("S:", "")
                        .replace("<|endoftext|>", "")
                        .replace("##", "")
                        .strip()
            )
            sentences = re.split(r'(?<=[.!?])\s+', clean_output)
            clean_output = " ".join(sentences[:3]) if len(sentences) > 1 else clean_output
            clean_output = " ".join(clean_output.split())
            print("Output:", clean_output)
            respond(clean_output)
        elif "exit" in command:
            should_run = False
        else:
            respond("Sorry, sir, I am not sure how to handle that command.")

def main():
    while should_run:
        command = listen_for_command()
        perform_command(command)
        time.sleep(1)
    respond("It was a great pleasure assisting you, sir.")

if __name__ == "__main__":
   main()
