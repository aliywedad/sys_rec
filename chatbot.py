import os
import tempfile
import speech_recognition as sr
import pygame
from gtts import gTTS
from mistralai.client import Mistral
from dotenv import load_dotenv

load_dotenv()

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
recognizer = sr.Recognizer()
conversation_history = []

pygame.mixer.init()


def speak(text: str):
    print(f"Assistant: {text}")
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name
    tts.save(tmp_path)
    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    os.remove(tmp_path)


def listen() -> str | None:
    with sr.Microphone() as source:
        print("\nListening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None

    try:
        text = recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        return None


def chat(user_input: str) -> str:
    conversation_history.append({"role": "user", "content": user_input})
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=conversation_history,
    )
    reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})
    return reply


def main():
    print("=== Voice Chatbot (Mistral AI) ===")
    print("Say 'quit', 'exit', or 'bye' to stop.\n")
    speak("Hello! I am your voice assistant powered by Mistral AI. How can I help you today?")

    while True:
        user_input = listen()

        if user_input is None:
            speak("I didn't catch that. Please try again.")
            continue

        if user_input.lower().strip() in {"quit", "exit", "bye", "stop", "goodbye"}:
            speak("Goodbye! Have a great day!")
            break

        response = chat(user_input)
        speak(response)


if __name__ == "__main__":
    main()
