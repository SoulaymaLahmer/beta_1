import pyttsx3
import speech_recognition as sr
import keyboard
import os
import subprocess as sp
import imdb
import wolframalpha
import google.generativeai as genai
import time
import threading
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from decouple import config
from datetime import datetime
from random import choice
from conv import random_text
from constants import USER, BOT
from utils import find_my_ip, search_on_google, search_on_wikipedia, youtube, send_email, get_news, weather_forecast, close_camera, take_photo,speak, set_alarm, is_valid_time_format,alarm_triggered

genai.configure(api_key="AIzaSyBa5w2uFKLiZexIf-HVdM0Bs5qqt8jtV9o")
model = genai.GenerativeModel('gemini-1.5-flash')

def set_volume(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(level / 100, None)

def set_brightness(level):
    sbc.set_brightness(level)

def greet_me():
    hour = datetime.now().hour
    if hour >= 6 and hour < 12:
        speak(f"Good Morning {USER}")
    if hour >= 12 and hour < 16:
        speak(f"Good Afternoon {USER}")
    elif hour >= 16 and hour < 20:
        speak(f"Good Evening {USER}")
    speak(f"I am {BOT}. Please tell me how may I help you ? {USER}")


listening = True


def start_listening():
    global listening
    listening = True
    print("started listening")


def stop_listening():
    global listening
    listening = False
    print("stopped listening")

def get_gemini_response(query):
    try:
        response = model.generate_content(query)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return "I'm sorry, I couldn't process that request."

keyboard.add_hotkey('a', start_listening)
keyboard.add_hotkey('d', stop_listening)


def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        queri = r.recognize_google(audio, language='en-US')
        print(f"User said: {queri}\n")
        if 'stop' not in queri and 'exit' not in queri:
            speak(choice(random_text))
        else:
            hour = datetime.now().hour
            if hour >= 21 and hour < 6:
                speak("Good night, take care!")
            else:
                speak("Have a nice day!")
            exit()

    except Exception:
        speak("Sorry, I didn't get that. Please try again.")
        queri = 'None'
    return queri


if __name__ == '__main__':
    greet_me()
    while True:
        if listening:
            query = take_command().lower()
            if alarm_triggered:
                speak("Time to wake up!")
                alarm_triggered = False
            if "how are you" in query:
                speak("I am fine. What about you?")

            elif "set volume to" in query:
                try:
                    level = int(query.split("set volume to")[-1].strip().replace("%", ""))
                    set_volume(level)
                    speak(f"Volume set to {level} percent")
                except:
                    speak("Sorry, I couldn't set the volume.")

            elif "set the brightness to" in query:
                try:
                    level = int(query.split("set brightness to")[-1].strip().replace("%", ""))
                    set_brightness(level)
                    speak(f"Brightness set to {level} percent")
                except:
                    speak("Sorry, I couldn't set the brightness.")

            elif "open command prompt" in query:
                    speak("Opening command prompt")
                    os.system('start cmd')

            elif "open camera" in query:
                speak("Opening camera")
                sp.run('start microsoft.windows.camera:', shell=True)

            elif "open github" in query:
                speak("Opening github")
                github_path = r"C:\Users\LENOVO\Downloads\GitHubDesktopSetup-x64.exe"
                os.startfile(github_path)

            elif "open git" in query:
                speak("Opening git")
                git_path = r"C:\Users\LENOVO\Downloads\Git-2.47.0.2-64-bit.exe"
                os.startfile(git_path)

            elif "open discord" in query:
                speak("Opening discord")
                discord_path = r"C:\Users\LENOVO\Desktop\Discord.lnk"
                os.startfile(discord_path)
            elif "open spotify" in query:
                speak("Opening spotify")
                spotify_path = r"C:\Users\LENOVO\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Spotify.lnk"
                os.startfile(spotify_path)

            elif "ip address" in query:
                ip_address = find_my_ip()
                speak(
                    f"your ip address is {ip_address} "
                )
                print(f"your ip address is {ip_address} ")

            elif "open YouTube" in query:
                speak(f"what do you want to play on youtube {USER}?")
                video = take_command().lower()
                youtube(video)

            elif "open google" in query:
                speak(f"what do you want to search on google {USER}?")
                query = take_command().lower()
                search_on_google(query)

            elif "open wikipedia" in query:
                speak(f"what do you want to search on wikipedia {USER}?")
                search = take_command().lower()
                results = search_on_wikipedia(search)
                speak(f"According to Wikipedia: {results}")
                speak("I am printing in terminal ")
                print(results)

            elif "send an email" in query:
                speak("on what email address you want to send ?.Please enter in the terminal")
                receiver_add = input("Email address: ")
                speak("what should be the subject of the email ?")
                subject = take_command().capitalize()
                speak("what should be the body of the email ?")
                message = take_command().capitalize()
                if send_email(receiver_add, subject, message):
                    speak("Email has been sent")
                    print("Email has been sent")
                else:
                    speak("something went wrong")

            elif "give me news" in query:
                speak(f"i am reading out the latest headline of today")
                speak(get_news())
                speak("i am printing in terminal ")
                print(*get_news(), sep='\n')



            elif " weather" in query:
                ip_address = find_my_ip()
                speak("tell me the name of your city")
                city = input("Enter name of your city:")
                speak(f"getting weather for {city}")
                weather, temp, feels_like = weather_forecast(city)
                speak(f"the current temperature is {temp}")
                speak(f"also the weather report talks about {weather}")
                speak("i am printing weather info on screen")
                print(f"Description: {weather}\nTemperature: {temp}\nFeels like: {feels_like}")



            elif "movie" in query :
                movies_db = imdb.IMDb()
                speak("Tell me the movie title")
                text = take_command()
                movies = movies_db.search_movie(text)
                speak("Searching for " + text)
                top_movies = movies[:2]
                if not top_movies:
                    speak("Sorry, I couldn't find any movies with that title.")
                else:
                    speak("I found these:")
                for movie in top_movies:
                    title = movie.get("title", "Unknown Title")
                    speak(f"{title} ")
                    try:
                        info = movie.getID()
                        movie_info = movies_db.get_movie(info)
                        rating = movie_info.get("rating", "Not available")
                        cast = movie_info.get("cast", [])
                        actor = cast[0:5] if cast else ["Cast not available"]
                        plot = movie_info.get("plot outline", "Plot summary not available")
                        speak(f"{title} has IMDb rating of {rating}.")
                        speak(f"It stars {', '.join(str(a) for a in actor)}.")
                        speak(f"The plot summary is: {plot}")
                        print(
                            f"{title} has IMDb rating of {rating}. It stars {actor}. The plot summary is: {plot}")
                    except Exception as e:
                        speak(f"Could not retrieve full info for {title}")
                        print(f"Error retrieving info for {title}: {e}")


            elif "calculate" in query.lower():
                app_id = "RVAXKK-J4H7EW8KRE"
                client = wolframalpha.Client(app_id)
                calc_index = query.lower().find("calculate")
                text = query[calc_index + len("calculate"):].strip()
                if text:
                    try:
                        result = client.query(text)
                        ans = next(result.results).text
                        speak("The answer is: " + ans)
                        print("The answer is: " + ans)
                    except StopIteration:
                        speak("Sorry, I couldn't find any answers.")
                else:
                    speak("Please specify what to calculate.")


            elif any(kw in query.lower() for kw in ["what is", "who is", "which is"]):
                app_id = "RVAXKK-J4H7EW8KRE"
                client = wolframalpha.Client(app_id)
                lowered = query.lower()
                for kw in ["what is", "who is", "which is"]:
                    if kw in lowered:
                        kw_index = lowered.find(kw)
                        text = query[kw_index + len(kw):].strip()
                        break
                if text:
                    try:
                        result = client.query(text)
                        ans = next(result.results).text
                        speak("The answer is: " + ans)
                        print("The answer is: " + ans)
                    except StopIteration:
                        speak("Sorry, I couldn't find any answers.")
                else:
                    speak("Sorry, I couldn't understand the question.")

            elif "close camera" in query:
                speak("Closing camera")
                close_camera()

            elif "take photo" in query or "take a picture" in query:
                speak("Opening camera to take a photo. Press SPACE to capture.")
                take_photo()

            elif "set an alarm" in query:
                speak("Please enter the alarm time in HH:MM format (24-hour):")
                alarm_time = input("Enter alarm time (HH:MM): ")
                if is_valid_time_format(alarm_time):
                    set_alarm(alarm_time)
                    speak(f"Alarm set for {alarm_time}")
                else:
                    speak("Invalid time format. Please try again using HH:MM format.")

            else:
                gemini_response = get_gemini_response(query)
                gemini_response = gemini_response.replace("*", "")
                if gemini_response and gemini_response != "I'm sorry, I couldn't process that request.":
                    speak(gemini_response)
                    print(gemini_response)










