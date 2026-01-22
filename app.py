import os, re, datetime, threading, requests, wikipedia, pyttsx3, webbrowser, pyjokes, pywhatkit
from queue import Queue
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ----------------- TTS -----------------
engine = pyttsx3.init()
engine.setProperty('rate', 165)
engine.setProperty('volume', 1.0)
for v in engine.getProperty('voices'):
    if "female" in (v.name or "").lower():
        engine.setProperty('voice', v.id)
        break
_tts_q = Queue()
def _tts_worker():
    while True:
        text = _tts_q.get()
        try: engine.say(text); engine.runAndWait()
        except: pass
        finally: _tts_q.task_done()
threading.Thread(target=_tts_worker, daemon=True).start()
def speak_async(text):
    if text: _tts_q.put(text)

# ----------------- Context & History -----------------
WHATSAPP_CONTEXT = {"number": None, "message": None}
HISTORY = []
USERS = {}  # simple memory store { email: password }
LOGGED_IN = set()

# ----------------- Command Processing -----------------
def process_command(c: str):
    c = (c or "").strip()
    if not c: return "Please enter a command.", False

    shutdown_flag = False
    response = "Sorry Sir, I did not understand that command."

    # Greetings
    if any(g in c.lower() for g in ["hello", "hi", "hey"]):
        response = "Hello ! I am your assistant Swastik. How can I help you ?"
    if "thank you" in c.lower() or "thanks" in c.lower():
        response = "You're welcome ! If you need anything else, just let me know."
    # Shutdown
    if any(w in c.lower() for w in ["bye","shutdown","exit","quit"]):
        response = "Goodbye Sir. Shutting down systems."


    # Time & Date
    if "time" in c.lower():
        now = datetime.datetime.now().strftime("%I:%M %p")
        response = f"The current time is {now}."
    if "date" in c.lower():
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        response = f"Today is {today}."

    # Joke
    if "joke" in c.lower():
        response = pyjokes.get_joke()

    # Wikipedia
    if any(c.lower().startswith(x) for x in ["who is","what is","tell me about","wikipedia"]):
        topic = re.sub(r"^(who is|what is|tell me about|wikipedia)\s+", "", c, flags=re.I)
        try:
            summary = wikipedia.summary(topic, sentences=3)
            response = summary
        except: response = "Sorry, I couldn't find that topic."

    # Websites
    def open_site(url):
        try: webbrowser.open(url); return True
        except: return False

    if "open google" in c.lower():
        webbrowser.open("https://www.google.com"); response = "Opening Google."
    elif "open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com"); response = "Opening YouTube."
    elif "open google and search" in c.lower() or "search" in c.lower():
        q = c.split("search", 1)[1].strip() if "search" in c else ""
        if q:
            open_site(f"https://www.google.com/search?q={q.replace(' ', '+')}")
            response = f"Opening Google and searching for “{q}”."
        else:
            response = "What should I search for on Google?"
    elif "open youtube and search" in c.lower():
        q = c.split("search", 1)[1].strip()
        if q:
            open_site(f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}")
            response = f"Opening YouTube and searching for “{q}”."
        else:
            response = "What should I search for on YouTube?"
    elif c.lower().startswith("search google"):
        query = c.split("search google",1)[1].strip()
        webbrowser.open(f"https://www.google.com/search?q={query.replace(' ','+')}")
        response = f"Searching Google for {query}"
    elif c.lower().startswith("search youtube"):
        query = c.split("search youtube",1)[1].strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ','+')}")
        response = f"Searching YouTube for {query}"
    elif "canva" in c.lower():
        open_site("https://www.canva.com")
        response = "Opening Canva, Sir."
    elif "open whatsapp" in c.lower():
        webbrowser.open("https://web.whatsapp.com")
        response = "Opening WhatsApp Web."
    elif "open spotify" in c.lower():
        open_site("https://www.spotify.com")
        response = "Opening Spotify, Sir."
    elif "open github" in c.lower():
        open_site("https://www.github.com")
        response = "Opening GitHub, Sir."
    elif "open stackoverflow" in c.lower():
        open_site("https://stackoverflow.com")
        response = "Opening Stack Overflow, Sir."
    elif "open linkedin" in c.lower():
        open_site("https://www.linkedin.com")
        response = "Opening LinkedIn, Sir."
    elif "open facebook" in c.lower():
        open_site("https://www.facebook.com")
        response = "Opening Facebook, Sir."
    elif "open twitter" in c.lower():
        open_site("https://www.twitter.com")
        response = "Opening Twitter, Sir."
    elif "open instagram" in c.lower():
        open_site("https://www.instagram.com")
        response = "Opening Instagram, Sir."
    elif "open reddit" in c.lower():
        open_site("https://www.reddit.com")
        response = "Opening Reddit, Sir."
    elif "open netflix" in c.lower():
        open_site("https://www.netflix.com")
        response = "Opening Netflix, Sir."
    elif "open amazon" in c.lower():
        open_site("https://www.amazon.com")
        response = "Opening Amazon, Sir."
    elif "open ebay" in c.lower():
        open_site("https://www.ebay.com")
        response = "Opening eBay, Sir."
    elif "open quora" in c.lower():
        open_site("https://www.quora.com")
        response = "Opening Quora, Sir."
    elif "open gmail" in c.lower():
        open_site("https://mail.google.com")
        response = "Opening Gmail, Sir."
    elif "open yahoo mail" in c.lower():
        open_site("https://mail.yahoo.com")
        response = "Opening Yahoo Mail, Sir."
    elif "open outlook" in c.lower():
        open_site("https://outlook.live.com")
        response = "Opening Outlook, Sir."
    elif "open zoom" in c.lower():
        open_site("https://zoom.us")
        response = "Opening Zoom, Sir."
    elif "open teams" in c.lower():
        open_site("https://teams.microsoft.com")
        response = "Opening Microsoft Teams, Sir."
    elif "open slack" in c.lower():
        open_site("https://slack.com")
        response = "Opening Slack, Sir."
    elif "open trello" in c.lower():
        open_site("https://trello.com")
        response = "Opening Trello, Sir."
    elif "open asana" in c.lower():
        open_site("https://asana.com")
        response = "Opening Asana, Sir."
    elif "open notion" in c.lower():
        open_site("https://www.notion.so")
        response = "Opening Notion, Sir."
    elif "open dropbox" in c.lower():
        open_site("https://www.dropbox.com")
        response = "Opening Dropbox, Sir."
    elif "open drive" in c.lower():
        open_site("https://drive.google.com")
        response = "Opening Google Drive, Sir."
    elif "open calendar" in c.lower():
        open_site("https://calendar.google.com")
        response = "Opening Google Calendar, Sir."
    elif "open maps" in c.lower():
        open_site("https://maps.google.com")
        response = "Opening Google Maps, Sir."
    elif "open weather" in c.lower():
        open_site("https://www.weather.com")
        response = "Opening Weather, Sir."
    elif "open news" in c.lower():
        open_site("https://news.google.com")
        response = "Opening Google News, Sir."
    elif "open youtube studio" in c.lower():
        open_site("https://studio.youtube.com")
        response = "Opening YouTube Studio, Sir."
    elif "open adsense" in c.lower():
        open_site("https://www.google.com/adsense")
        response = "Opening Google AdSense, Sir."
    elif "open analytics" in c.lower():
        open_site("https://analytics.google.com")
        response = "Opening Google Analytics, Sir."
    elif "open search console" in c.lower():
        open_site("https://search.google.com/search-console")
        response = "Opening Google Search Console, Sir."
    # Play Song
    if c.lower().startswith("play"):
        song = c.split("play",1)[1].strip()
        if song:
            try:
                pywhatkit.playonyt(song)
                response = f"Playing {song} on YouTube."
            except Exception as e:
                response = f"Failed to play {song}: {str(e)}"
        else:
            response = "Please specify a song to play."

    # Add to history
    HISTORY.append({"time": datetime.datetime.now().strftime("%H:%M:%S"), "command": c, "response": response})
    speak_async(response)
    return response, shutdown_flag

# ----------------- Routes -----------------
@app.route("/command", methods=["POST"])
def handle_command():
    data = request.json
    command = data.get("command","")
    response, shutdown_flag = process_command(command)
    if shutdown_flag:
        threading.Thread(target=lambda: os._exit(0), daemon=True).start()
    return jsonify({"response": response})

@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(HISTORY)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email"); pw = data.get("password")
    if not email or not pw:
        return jsonify({"success": False, "msg": "Missing fields"})
    if email in USERS:
        return jsonify({"success": False, "msg": "User already exists"})
    USERS[email] = pw
    return jsonify({"success": True, "msg": "Signup successful"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email"); pw = data.get("password")
    if USERS.get(email) == pw:
        LOGGED_IN.add(email)
        return jsonify({"success": True, "msg": "Login successful"})
    return jsonify({"success": False, "msg": "Invalid credentials"})

@app.route("/welcome", methods=["GET"])
def welcome():
    txt = "Good morning Sir! I am your assistant Swastik."
    speak_async(txt)
    return jsonify({"welcome_text": txt})

if __name__ == "__main__":
    app.run(debug=True)
