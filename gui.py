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
import re
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from decouple import config
from datetime import datetime
from random import choice
import tkinter as tk
from tkinter import scrolledtext, ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from PIL import Image, ImageTk
from conv import random_text
from constants import USER, BOT,GEMINI_API_KEY
from utils import find_my_ip, search_on_google, search_on_wikipedia, youtube, send_email, get_news, weather_forecast, close_camera, take_photo, set_alarm, is_valid_time_format, alarm_triggered, set_volume

# Initialize global pyttsx3 engine with custom voice settings
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "Zira" in voice.name:  # Select Microsoft Zira Desktop (female voice)
        engine.setProperty('voice', voice.id)
        break
    else:
        engine.setProperty('voice', voices[0].id)  # Fallback to first available voice
        engine.setProperty('rate', 200)
        engine.setProperty('volume', 0.9)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

listening = False
gui_app = None  # Global reference to GUI for thread-safe updates

def greet_me():
    hour = datetime.now().hour
    greeting = ""
    if hour >= 6 and hour < 12:
        greeting = f"Good Morning {USER}"
    elif hour >= 12 and hour < 16:
        greeting = f"Good Afternoon {USER}"
    elif hour >= 16 and hour < 20:
        greeting = f"Good Evening {USER}"
    else:
        greeting = f"Good Night {USER}"
    greeting += f"\nI am {BOT}. How may I assist you today, {USER}?"
    speak(greeting)
    if gui_app:
        gui_app.update_conversation(f"{BOT}: {greeting}\n")

def start_listening():
    global listening
    listening = True
    print("Started listening")
    if gui_app:
        gui_app.update_status("Listening")
        gui_app.toggle_listening_button(True)

def stop_listening():
    global listening
    listening = False
    print("Stopped listening")
    if gui_app:
        gui_app.update_status("Stopped")
        gui_app.toggle_listening_button(False)

def stop_speaking():
    """Stop the current speech output."""
    engine.stop()
    if gui_app:
        gui_app.update_conversation(f"{BOT}: Speech stopped.\n")

def get_gemini_response(query):
    try:
        response = model.generate_content(query)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return "I'm sorry, I couldn't process that request."

def speak(text):
    """Speak the given text using the global pyttsx3 engine."""
    engine.say(text)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        if gui_app:
            gui_app.update_status("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        if gui_app:
            gui_app.update_status("Recognizing...")
        queri = r.recognize_google(audio, language='en-US')
        print(f"User said: {queri}\n")
        if gui_app:
            gui_app.update_conversation(f"{USER}: {queri}\n")
        if 'stop' not in queri.lower() and 'exit' not in queri.lower():
            speak(choice(random_text))
        else:
            hour = datetime.now().hour
            farewell = "Good night, take care!" if hour >= 21 or hour < 6 else "Have a nice day!"
            speak(farewell)
            if gui_app:
                gui_app.update_conversation(f"{BOT}: {farewell}\n")
            return "exit"
    except Exception:
        error_msg = "Sorry, I didn't get that. Please try again."
        speak(error_msg)
        if gui_app:
            gui_app.update_conversation(f"{BOT}: {error_msg}\n")
        return 'None'
    return queri

def process_command(query):
    global alarm_triggered
    query = query.lower()
    if gui_app:
        gui_app.update_conversation(f"{BOT}: Processing command: {query}\n")

    if alarm_triggered:
        speak("Time to wake up!")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Time to wake up!\n")
        alarm_triggered = False

    if "how are you" in query:
        response = "I am fine. What about you?"
        speak(response)
        if gui_app:
            gui_app.update_conversation(f"{BOT}: {response}\n")

    elif "set volume to" in query:
        try:
            level = int(query.split("set volume to")[-1].strip().replace("%", ""))
            set_volume(level)
            response = f"Volume set to {level} percent"
            speak(response)
            if gui_app:
                gui_app.update_conversation(f"{BOT}: {response}\n")
                gui_app.update_volume_slider(level)
        except:
            response = "Sorry, I couldn't set the volume."
            speak(response)
            if gui_app:
                gui_app.update_conversation(f"{BOT}: {response}\n")

    elif "open command prompt" in query:
        speak("Opening command prompt")
        os.system('start cmd')
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Opening command prompt\n")

    elif "open camera" in query:
        speak("Opening camera")
        sp.run('start microsoft.windows.camera:', shell=True)
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Opening camera\n")

    elif "open github" in query:
        speak("Opening github")
        github_path = r"C:\Users\LENOVO\Downloads\GitHubDesktopSetup-x64.exe"
        os.startfile(github_path)
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Opening github\n")

    elif "open git" in query:
        speak("Opening git")
        git_path = r"C:\Users\LENOVO\Downloads\Git-2.47.0.2-64-bit.exe"
        os.startfile(git_path)
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Opening git\n")

    elif "open discord" in query:
        speak("Opening discord")
        discord_path = r"C:\Users\LENOVO\Desktop\Discord.lnk"
        os.startfile(discord_path)
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Opening discord\n")

    elif "open spotify" in query:
        speak("Opening spotify")
        spotify_path = r"C:\Users\LENOVO\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Spotify.lnk"
        os.startfile(spotify_path)
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Opening spotify\n")

    elif "ip address" in query:
        ip_address = find_my_ip()
        response = f"Your IP address is {ip_address}"
        speak(response)
        print(response)
        if gui_app:
            gui_app.update_conversation(f"{BOT}: {response}\n")

    elif "open youtube" in query:
        speak(f"What do you want to play on YouTube, {USER}?")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: What do you want to play on YouTube, {USER}?\n")
        video = take_command().lower()
        if video != 'None' and video != 'exit':
            youtube(video)
            if gui_app:
                gui_app.update_conversation(f"{BOT}: Playing {video} on YouTube\n")
        return video

    elif "open google" in query:
        speak(f"What do you want to search on Google, {USER}?")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: What do you want to search on Google, {USER}?\n")
        query = take_command().lower()
        if query != 'None' and query != 'exit':
            search_on_google(query)
            if gui_app:
                gui_app.update_conversation(f"{BOT}: Searching {query} on Google\n")
        return query

    elif "open wikipedia" in query:
        speak(f"What do you want to search on Wikipedia, {USER}?")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: What do you want to search on Wikipedia, {USER}?\n")
        search = take_command().lower()
        if search != 'None' and search != 'exit':
            results = search_on_wikipedia(search)
            speak(f"According to Wikipedia: {results}")
            speak("I am printing in terminal")
            print(results)
            if gui_app:
                gui_app.update_conversation(f"{BOT}: According to Wikipedia: {results}\n")
        return search

    elif "send an email" in query:
        speak("On what email address do you want to send? Please enter in the terminal")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: On what email address do you want to send? Please enter in the terminal\n")
        receiver_add = input("Email address: ")
        speak("What should be the subject of the email?")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: What should be the subject of the email?\n")
        subject = take_command().capitalize()
        speak("What should be the body of the email?")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: What should be the body of the email?\n")
        message = take_command().capitalize()
        if send_email(receiver_add, subject, message):
            speak("Email has been sent")
            print("Email has been sent")
            if gui_app:
                gui_app.update_conversation(f"{BOT}: Email has been sent\n")
        else:
            speak("Something went wrong")
            if gui_app:
                gui_app.update_conversation(f"{BOT}: Something went wrong\n")

    elif "give me news" in query:
        speak("I am reading out the latest headline of today")
        news = get_news()
        speak(news)
        speak("I am printing in terminal")
        print(*news, sep='\n')
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Latest headlines:\n" + "\n".join(news) + "\n")

    elif "weather" in query:
        ip_address = find_my_ip()
        speak("Tell me the name of your city")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Tell me the name of your city\n")
        city = input("Enter name of your city: ")
        speak(f"Getting weather for {city}")
        weather, temp, feels_like = weather_forecast(city)
        speak(f"The current temperature is {temp}")
        speak(f"Also the weather report talks about {weather}")
        speak("I am printing weather info on screen")
        print(f"Description: {weather}\nTemperature: {temp}\nFeels like: {feels_like}")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Weather for {city}\nDescription: {weather}\nTemperature: {temp}\nFeels like: {feels_like}\n")

    elif "movie" in query:
        movies_db = imdb.IMDb()
        speak("Tell me the movie title")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Tell me the movie title\n")
        text = take_command()
        if text != 'None' and text != 'exit':
            movies = movies_db.search_movie(text)
            speak("Searching for " + text)
            top_movies = movies[:2]
            if not top_movies:
                speak("Sorry, I couldn't find any movies with that title.")
                if gui_app:
                    gui_app.update_conversation(f"{BOT}: Sorry, I couldn't find any movies with that title.\n")
            else:
                speak("I found these:")
                if gui_app:
                    gui_app.update_conversation(f"{BOT}: I found these:\n")
                for movie in top_movies:
                    title = movie.get("title", "Unknown Title")
                    speak(f"{title}")
                    try:
                        info = movie.getID()
                        movie_info = movies_db.get_movie(info)
                        rating = movie_info.get("rating", "Not available")
                        cast = movie_info.get("cast", [])
                        actor = cast[0:5] if cast else ["Cast not available"]
                        plot = movie_info.get("plot outline", "Plot summary not available")
                        response = f"{title} has IMDb rating of {rating}. It stars {', '.join(str(a) for a in actor)}. The plot summary is: {plot}"
                        speak(response)
                        print(response)
                        if gui_app:
                            gui_app.update_conversation(f"{BOT}: {response}\n")
                    except Exception as e:
                        speak(f"Could not retrieve full info for {title}")
                        print(f"Error retrieving info for {title}: {e}")
                        if gui_app:
                            gui_app.update_conversation(f"{BOT}: Could not retrieve full info for {title}\n")
        return text

    elif "calculate" in query:
        app_id = "RVAXKK-J4H7EW8KRE"
        client = wolframalpha.Client(app_id)
        calc_index = query.find("calculate")
        text = query[calc_index + len("calculate"):].strip()
        if text:
            try:
                result = client.query(text)
                ans = next(result.results).text
                speak("The answer is: " + ans)
                print("The answer is: " + ans)
                if gui_app:
                    gui_app.update_conversation(f"{BOT}: The answer is: {ans}\n")
            except StopIteration:
                speak("Sorry, I couldn't find any answers.")
                if gui_app:
                    gui_app.update_conversation(f"{BOT}: Sorry, I couldn't find any answers.\n")
        else:
            speak("Please specify what to calculate.")
            if gui_app:
                gui_app.update_conversation(f"{BOT}: Please specify what to calculate.\n")

    elif any(kw in query for kw in ["what is", "who is", "which is"]):
        app_id = "RVAXKK-J4H7EW8KRE"
        client = wolframalpha.Client(app_id)
        for kw in ["what is", "who is", "which is"]:
            if kw in query:
                kw_index = query.find(kw)
                text = query[kw_index + len(kw):].strip()
                break
        if text:
            try:
                result = client.query(text)
                ans = next(result.results).text
                speak("The answer is: " + ans)
                print("The answer is: " + ans)
                if gui_app:
                    gui_app.update_conversation(f"{BOT}: The answer is: {ans}\n")
            except StopIteration:
                speak("Sorry, I couldn't find any answers.")
                if gui_app:
                    gui_app.update_conversation(f"{BOT}: Sorry, I couldn't find any answers.\n")
        else:
            speak("Sorry, I couldn't understand the question.")
            if gui_app:
                gui_app.update_conversation(f"{BOT}: Sorry, I couldn't understand the question.\n")

    elif "close camera" in query:
        speak("Closing camera")
        close_camera()
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Closing camera\n")

    elif "take a photo" in query or "take a picture" in query:
        speak("Opening camera to take a photo. Press SPACE to capture.")
        take_photo()
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Opening camera to take a photo. Press SPACE to capture.\n")

    elif "set an alarm" in query:
        speak("Please enter the alarm time in HH:MM format (24-hour):")
        if gui_app:
            gui_app.update_conversation(f"{BOT}: Please enter the alarm time in HH:MM format (24-hour):\n")
        alarm_time = input("Enter alarm time (HH:MM): ")
        if is_valid_time_format(alarm_time):
            set_alarm(alarm_time)
            speak(f"Alarm set for {alarm_time}")
            if gui_app:
                gui_app.update_conversation(f"{BOT}: Alarm set for {alarm_time}\n")
        else:
            speak("Invalid time format. Please try again using HH:MM format.")
            if gui_app:
                gui_app.update_conversation(f"{BOT}: Invalid time format. Please try again using HH:MM format.\n")

    else:
        gemini_response = get_gemini_response(query)
        gemini_response = gemini_response.replace("*", "")
        if gemini_response and gemini_response != "I'm sorry, I couldn't process that request.":
            speak(gemini_response)
            print(gemini_response)
            if gui_app:
                gui_app.update_conversation(f"{BOT}: {gemini_response}\n")
        else:
            speak(gemini_response)
            if gui_app:
                gui_app.update_conversation(f"{BOT}: {gemini_response}\n")

def voice_loop():
    global listening
    while True:
        if listening:
            query = take_command()
            if query == "exit":
                break
            if query != 'None':
                process_command(query)
        time.sleep(0.1)  # Prevent CPU overuse


class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{BOT} - AI Assistant")
        self.root.geometry("700x500")
        self.style = ttkb.Style(theme='darkly')  # Modern dark theme



        # Load background image
        #try:
        bg_image = Image.open("background.jpg")
        bg_image = bg_image.resize((700, 500), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        #except Exception as e:
           # print(f"Error loading background image: {e}")
            #self.root.configure(bg='#1c2526')  # Fallback background color

        # Main frame with semi-transparent background
        self.main_frame = ttk.Frame(self.root, padding=10, style='TFrame')
        self.main_frame.pack(fill=BOTH, expand=True)
        self.style.configure('TFrame', background='#2b2b2b', alpha=0.8)

        # Title label
        self.title_label = ttk.Label(
            self.main_frame, text=f"{BOT} - Your AI Assistant", font=('Segoe UI', 16, 'bold'),
            foreground='#00b7eb', background='#2b2b2b'
        )
        self.title_label.pack(pady=10)

        # Conversation display
        self.conversation = scrolledtext.ScrolledText(
            self.main_frame, wrap=tk.WORD, height=18, font=('Segoe UI', 11),
            bg='#1e1e1e', fg='#e0e0e0', insertbackground='white', relief='flat'
        )
        self.conversation.pack(padx=10, pady=10, fill=BOTH, expand=True)
        self.conversation.configure(state='disabled')
        ToolTip(self.conversation, "Conversation history")

        # Status frame
        self.status_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.status_frame.pack(fill=X, pady=5)
        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = ttk.Label(
            self.status_frame, textvariable=self.status_var, font=('Segoe UI', 10, 'italic'),
            foreground='#00ff00' if self.status_var.get() == "Listening" else '#ff0000',
            background='#2b2b2b'
        )
        self.status_label.pack(side=LEFT)
        self.mic_icon = ttk.Label(self.status_frame, text="🎤", font=('Segoe UI', 12), background='#2b2b2b')
        self.mic_icon.pack(side=LEFT, padx=5)
        self.animate_status()

        # Control frame
        self.control_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.control_frame.pack(fill=X, pady=10)

        # Listening toggle button
        self.listening_var = tk.BooleanVar(value=False)
        self.listen_button = ttk.Checkbutton(
            self.control_frame, text="Listen", style='primary.Roundtoggle.TCheckbutton',
            variable=self.listening_var, command=self.toggle_listening, width=12
        )
        self.listen_button.pack(side=LEFT, padx=5)
        ToolTip(self.listen_button, "Toggle voice input (Hotkeys: A to start, D to stop)")

        # Stop talking button
        self.stop_talking_button = ttk.Button(
            self.control_frame, text="Stop Talking", style='danger.Outline.TButton',
            command=stop_speaking, width=12
        )
        self.stop_talking_button.pack(side=LEFT, padx=5)
        ToolTip(self.stop_talking_button, "Stop Beta's current speech")

        # Clear conversation button
        self.clear_button = ttk.Button(
            self.control_frame, text="Clear Chat", style='secondary.Outline.TButton',
            command=self.clear_conversation, width=12
        )
        self.clear_button.pack(side=LEFT, padx=5)
        ToolTip(self.clear_button, "Clear conversation history")

        # Settings button
        self.settings_button = ttk.Button(
            self.control_frame, text="Settings", style='info.Outline.TButton',
            command=self.toggle_settings, width=12
        )
        self.settings_button.pack(side=LEFT, padx=5)
        ToolTip(self.settings_button, "Open settings panel")

        # Text input
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            self.main_frame, textvariable=self.input_var, width=50, font=('Segoe UI', 11),
            style='primary.TEntry'
        )
        self.input_entry.pack(pady=10, fill=X, padx=10)
        self.input_entry.bind("<Return>", self.process_text_command)
        ToolTip(self.input_entry, "Type a command and press Enter")

        # Settings panel (initially hidden)
        self.settings_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.volume_label = ttk.Label(
            self.settings_frame, text="Volume:", font=('Segoe UI', 10), background='#2b2b2b'
        )
        self.volume_label.pack(side=LEFT, padx=5)
        self.volume_var = tk.IntVar(value=50)  # Default volume
        self.volume_slider = ttk.Scale(
            self.settings_frame, from_=0, to=100, orient=HORIZONTAL,
            variable=self.volume_var, command=self.adjust_volume, style='primary.Horizontal.TScale'
        )
        self.volume_slider.pack(side=LEFT, padx=5, fill=X, expand=True)
        ToolTip(self.volume_slider, "Adjust system volume")

    def update_conversation(self, text):
        self.conversation.configure(state='normal')
        self.conversation.insert(tk.END, text)
        self.conversation.see(tk.END)
        self.conversation.configure(state='disabled')

    def update_status(self, status):
        self.status_var.set(status)
        self.status_label.configure(
            foreground='#00ff00' if status.startswith("Listening") else '#ff0000' if status == "Stopped" else '#ffa500'
        )

    def toggle_listening(self):
        if self.listening_var.get():
            start_listening()
        else:
            stop_listening()

    def toggle_listening_button(self, is_listening):
        self.listening_var.set(is_listening)
        self.mic_icon.configure(text="🎤" if is_listening else "🔇")

    def clear_conversation(self):
        self.conversation.configure(state='normal')
        self.conversation.delete(1.0, tk.END)
        self.conversation.configure(state='disabled')
        self.update_conversation(f"{BOT}: Conversation cleared.\n")

    def toggle_settings(self):
        if self.settings_frame.winfo_ismapped():
            self.settings_frame.pack_forget()
            self.settings_button.configure(text="Settings")
        else:
            self.settings_frame.pack(fill=X, pady=5)
            self.settings_button.configure(text="Hide Settings")

    def adjust_volume(self, *args):
        volume = int(self.volume_var.get())
        set_volume(volume)
        self.update_conversation(f"{BOT}: Volume set to {volume}%\n")

    def update_volume_slider(self, volume):
        self.volume_var.set(volume)

    def process_text_command(self, event=None):
        query = self.input_var.get().strip()
        if query:
            self.update_conversation(f"YOU: {query}\n")
            self.input_var.set("")  # Clear input
            threading.Thread(target=process_command, args=(query,), daemon=True).start()

    def animate_status(self):
        if self.status_var.get().startswith("Listening"):
            current = self.status_var.get()
            dots = current.count(".")
            next_dots = "." * ((dots + 1) % 4)
            self.status_var.set(f"Listening{next_dots}")
            self.root.after(500, self.animate_status)
        elif self.status_var.get().startswith("Recognizing"):
            current = self.status_var.get()
            dots = current.count(".")
            next_dots = "." * ((dots + 1) % 4)
            self.status_var.set(f"Recognizing{next_dots}")
            self.root.after(500, self.animate_status)

if __name__ == '__main__':
    # Initialize GUI
    root = ttkb.Window(themename='darkly')
    gui_app = AssistantGUI(root)
    greet_me()

    # Register hotkeys
    keyboard.add_hotkey('a', start_listening)
    keyboard.add_hotkey('d', stop_listening)

    # Start voice loop in a separate thread
    voice_thread = threading.Thread(target=voice_loop, daemon=True)
    voice_thread.start()

    # Start GUI main loop
    root.mainloop()
