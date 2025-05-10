from idlelib import query
import cv2
import ctypes
import pygame
import pyttsx3
import speech_recognition as sr
import requests
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import pywhatkit as kit
from email.message import EmailMessage
import smtplib
import gtts
import os
import time
from datetime import datetime
import threading
from decouple import config
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound
from constants import(
    EMAIL,
    PASSWORD,
    IP_ADDR_API_URL,
    NEWS_FETCH_API_URL,
    NEWS_FETCH_API_KEY,
    WEATHER_FORECAST_API_URL,
    WEATHER_FORECAST_API_KEY,
    SMTP_URL,
    SMTP_PORT,
)

engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 225)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

speak_lock = threading.Lock()

def speak(text):
    with speak_lock:
        engine.say(text)
        engine.runAndWait()


def is_valid_time_format(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


alarm_triggered = False  # Global or outer-scope variable

def set_alarm(alarm_time_str):
    def alarm():
        while True:
            current_time = datetime.now().strftime("%H:%M")
            if current_time == alarm_time_str:
                print("⏰ Alarm ringing!")
                play_alarm_sound()
                break
            time.sleep(1)

    threading.Thread(target=alarm).start()

def play_alarm_sound():
    pygame.mixer.init()
    pygame.mixer.music.load(r"C:\Users\LENOVO\Desktop\BETA_3\alarm.mp3")  # Use .mp3 or .wav
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass  # Keeps script running while the sound plays

def set_volume(level):
    volume = max(0, min(level, 100))  # Clamp between 0-100
    devices = ctypes.windll.user32.SendMessageW
    # Use pycaw or third-party libs for per-app or device-specific control
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
    from pycaw.utils import AudioUtilities

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
    volume_interface.SetMasterVolumeLevelScalar(volume / 100.0, None)



def take_photo():
    cam = cv2.VideoCapture(0)  # 0 is usually the default webcam
    cv2.namedWindow("Press SPACE to capture photo", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Press SPACE to capture photo", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "captured_photo.png"
            cv2.imwrite(img_name, frame)
            print(f"{img_name} saved!")
            speak("Photo captured and saved.")
            break

    cam.release()
    cv2.destroyAllWindows()

def close_camera():
    os.system("taskkill /im WindowsCamera.exe /f")


def find_my_ip():
    ip_address = requests.get("https://api.ipify.org?format=json").json()
    return ip_address['ip']

def search_on_wikipedia(query):
    try:
        results = wikipedia.summary(query, sentences=2)
        return results
    except DisambiguationError as e:
        # L'utilisateur doit choisir ou raffiner sa recherche
        return f"The term '{query}' is ambiguous. Some options are: {', '.join(e.options[:5])}."
    except PageError:
        return "Sorry, I could not find any matching page."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def search_on_google(query):
    kit.search(query)

def youtube (video):
    kit.playonyt(video)

def send_email(receiver_add, subject, message):
    try:
        email = EmailMessage()
        email['To'] = receiver_add
        email['From'] = EMAIL
        email['Subject'] = subject
        email.set_content(message)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(EMAIL, PASSWORD)
        s.send_message(email)
        s.close()
        return True
    except Exception as e:
        print(e)
        return False

def get_news():
    news_headlines = []
    result = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&category=general&apiKey=016fdfd2b5024ce998dea16594bd34ba").json()
    articles = result["articles"]
    for article in articles:
        news_headlines.append(article["title"])
    return news_headlines[:5]

def weather_forecast(city):
    res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=e62c1db91540f72f9f158faf0cb2c83e").json()
    weather = res["weather"][0]["main"]
    temp = res["main"]["temp"]
    feels_like = res["main"]["feels_like"]
    return weather, f"{temp}°C", f"{feels_like}°C"