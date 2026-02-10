# CHANGE = your_ai_name

import datetime
import random

import pyautogui
import speech_recognition as sr
import os
import webbrowser
import threading
import time



WAKE_WORDS = ["hey your_ai_name", "heyyour_ai_name", "your_ai_name"]
history = []
scrolling = False
waiting_message_for = None



def speak(text):
    print("your_ai_name:", text)

    text = text.replace(":", " ")
    text = text.replace(".", " . ")
    text = text.replace(",", " , ")

    os.system(f'say -r 185 -v Samantha "{text}"')


def listen(timeout=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, phrase_time_limit=timeout)

    try:
        text = r.recognize_google(audio, language="en-US")
        print("You:", text)
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("There is a problem with the internet.")
        return ""


def scroll_worker(direction):
    global scrolling

    key = 125 if direction == "down" else 126

    start = time.time()

    while scrolling:
        if time.time() - start > 5:
            scrolling = False
            break

        os.system(f"""
        osascript -e 'tell application "Google Chrome" to activate' \
                  -e 'tell application "System Events" to key code {key}'
        """)
        time.sleep(0.5)



def greet():
    answers = [
        "Hello. I'm listening.",
        "Hi. How can I help you?",
        "Go ahead, I'm listening."
    ]
    return random.choice(answers)


def get_time():
    now = datetime.datetime.now()
    return f"The time is {now.hour} {now.minute}."


def help_menu():
    return "I can greet you, tell the time, and stop when you say exit."


def fallback():
    return "Sorry, I didn't understand."


def detect_intent(text: str):
    if any(w in text for w in ["hello", "hi"]):
        return "greet"

    if any(w in text for w in [
        "time",
        "clock",
        "hour"
    ]):
        return "time"

    if "help" in text:
        return "help"

    if "exit" in text or "stop go" in text:
        return "exit"

    if "youtube" in text:
        return "youtube"

    if "google" in text:
        return "google"

    if "telegram" in text:
        return "telegram"

    if "back" in text:
        return "back"

    if "scroll up" in text:
        return "scroll_up"

    if "scroll down" in text:
        return "scroll_down"

    if "scroll stop" in text or "stop scrolling" in text:
        return "scroll_stop"

    if "send" in text and "message" in text and "to" in text:
        return "send_message"

    return "unknown"


def handle_intent(intent, user_text):
    global scrolling
    global waiting_message_for

    if intent == "greet":
        return greet()

    if intent == "time":
        return get_time()

    if intent == "help":
        return help_menu()

    if intent == "youtube":
        url = "https://youtube.com"
        history.append(url)
        webbrowser.open(url)
        return "Opening YouTube."

    if intent == "google":
        url = "https://google.com"
        history.append(url)
        webbrowser.open(url)
        return "Opening Google."

    if intent == "telegram":
        url = "https://web.telegram.org"
        history.append(url)
        webbrowser.open(url)
        return "Opening Telegram."

    if intent == "back":
        os.system("""
        osascript -e 'tell application "Google Chrome" to activate' \
                  -e 'tell application "System Events" to keystroke "w" using command down'
        """)
        return "Closing current tab."

    if intent == "scroll_down":
        if not scrolling:
            scrolling = True
            threading.Thread(target=scroll_worker, args=("down",), daemon=True).start()
        return "Scrolling down."

    if intent == "scroll_up":
        if not scrolling:
            scrolling = True
            threading.Thread(target=scroll_worker, args=("up",), daemon=True).start()
        return "Scrolling up."

    if intent == "scroll_stop":
        scrolling = False
        return "Stopped scrolling."

    if intent == "send_message":
        try:
            name = user_text.split("to", 1)[1].strip().split()[0]
            waiting_message_for = name
            return f"What should I write to {name}?"
        except:
            return "Whom should I send it to?"

    return fallback()



def main():
    global waiting_message_for
    speak("your_ai_name listened")

    active = False

    while True:
        msg = listen()

        if not msg:
            continue

        if not active:
            if any(w in msg for w in WAKE_WORDS):
                active = True
                speak("I'm listening")
            continue


        if waiting_message_for:
            name = waiting_message_for
            message = msg

            speak(f"Sending message to {name}")

            os.system("open -a 'Telegram'")
            time.sleep(3)

            pyautogui.hotkey("command", "k")
            time.sleep(1)

            pyautogui.press("enter")
            time.sleep(2)


            for _ in range(8):
                pyautogui.press("tab")
                time.sleep(0.2)

            pyautogui.write(message, interval=0.03)
            time.sleep(0.3)

            pyautogui.press("enter")

            waiting_message_for = None
            speak("Message sent.")
            continue

        intent = detect_intent(msg)

        if intent == "exit":
            speak("Goodbye!")
            active = False
            continue    

        speak(handle_intent(intent, msg))


if __name__ == "__main__":
    main()


