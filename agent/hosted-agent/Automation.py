from webbrowser import open as webopen  # Open web URLs
from pywhatkit import search, playonyt  # Google search & YouTube
from dotenv import dotenv_values  # Load environment variables
from bs4 import BeautifulSoup  # HTML parsing
from rich import print
from groq import Groq  # AI chat
import webbrowser  # Open URLs
import subprocess  # System interactions
import requests  # HTTP requests
import keyboard  # Keyboard actions
import asyncio  # Async programming
import os  # OS functions
import json  # JSON parsing

# Load environment variables from .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define CSS classes for parsing specific elements
classes = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "ZØLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

# User-agent for HTTP requests
useragent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' 
             '(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36')

# Initialize Groq AI client if key is present
client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None


# Predefined professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

# Chatbot messages storage
messages = []

# System message for chatbot
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am Navjeet, You're a content writer. You create various content forms like letters, codes, applications, essays, notes, songs, and poems."
}]

# Function for Google Search
def GoogleSearch(Topic):
    search(Topic)
    print(f"[OMNIS Automation] Searching {Topic} on Google")
    return True

# Function to create content using AI and save to a file
def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(["notepad.exe", File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b", messages=SystemChatBot + messages,
            max_tokens=2048, temperature=0.7, top_p=1, stream=True, stop=None
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})
        print(f"[OMNIS Automation] Content created successfully.")
        return answer

    Topic = Topic.replace("Content ", "").strip()
    content_by_ai = ContentWriterAI(Topic)
    file_path = os.path.join("Data", f"{Topic.lower().replace(' ', '_')}.txt")
    os.makedirs("Data", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content_by_ai)
    OpenNotepad(file_path)
    return True

# Function to search on YouTube
def youtubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    print(f"[OMNIS Automation] Searching {Topic} on YouTube")
    return True

# Function to play a video on YouTube
def PlayYoutube(query):
    playonyt(query)
    print(f"[OMNIS Automation] Playing {query} on YouTube")
    return True


# Function to open a website
def OpenApp(app):
    try:
        app = app.lower().strip()

        # Dictionary of common websites
        websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "chrome": "https://www.google.com",
            "browser": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "chatgpt": "https://chatgpt.com",
            "github": "https://github.com",
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "whatsapp": "https://web.whatsapp.com",
            "linkedin": "https://www.linkedin.com",
            "amazon": "https://www.amazon.in",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com",
            "stackoverflow": "https://stackoverflow.com",
            "reddit": "https://www.reddit.com",
            "x": "https://x.com",
            "twitter": "https://x.com"
        }

        if app in websites:
            webbrowser.open_new_tab(websites[app])
            print(f"[OMNIS Automation] Opening {app}")
            return True
        elif app.startswith("http://") or app.startswith("https://"):
            webbrowser.open_new_tab(app)
            print(f"[OMNIS Automation] Opening {app}")
            return True
        elif "." in app and " " not in app:
            webbrowser.open_new_tab(f"https://{app}")
            print(f"[OMNIS Automation] Opening {app}")
            return True
        else:
            search_url = (
                "https://www.google.com/search?q="
                + requests.utils.quote(app)
            )
            webbrowser.open_new_tab(search_url)
            print(f"[OMNIS Automation] Opening {app}")
            return True

    except Exception as e:
        print(f"Error opening {app}: {e}")
        return False


def CloseApp(app):
    try:
        app_name = app.lower().strip()
        if not app_name.endswith(".exe"):
            app_name += ".exe"
        subprocess.run(["taskkill", "/f", "/im", app_name], capture_output=True, shell=True)
        print(f"[OMNIS Automation] Closing {app}")
        return True
    except Exception:
        return False
# Function to execute system commands
def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "up": lambda: keyboard.press_and_release("volume up"),
        "down": lambda: keyboard.press_and_release("volume down"),
        "shutdown": lambda: os.system("shutdown /s /t 0"),
        "sleep": lambda: os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0"),
        "restart": lambda: os.system("shutdown /r /t 0"),
        "cancel shutdown": lambda: os.system("shutdown /a"),
    }
    if command in actions:
        actions[command]()
        return True
    return False

# =========================
# AI COMMAND GENERATOR
# =========================

def GenerateCommands(user_prompt):
    system_prompt = """
You are O.M.N.I.S AI Command Generator.

Understand user prompts in Hindi, Hinglish and English.
Convert the user's intention into commands supported by the Python app.

Return ONLY a valid JSON object in this format:
{
    "commands": ["command 1", "command 2"],
    "message": "short response"
}

ALLOWED COMMAND FORMATS:

1. Open app:
   open chrome
   open notepad
   open calculator

2. Close app:
   close notepad

3. Play YouTube:
   play Arijit Singh songs

4. Google search:
   search on google Python tutorials

5. YouTube search:
   search on youtube Python tutorials

6. Amazon search:
   search on amazon gaming mouse

7. Flipkart search:
   search on flipkart Samsung phone

8. Generate content:
   content advantages of cybersecurity

9. Open website:
   go to github.com

10. System commands:
   system volume up
   system volume down
   system mute
   system unmute
   system shutdown
   system restart
   system sleep
   system cancel shutdown

RULES:
- Return only commands from the supported formats above.
- Never generate Python code, shell commands or arbitrary instructions.
- Never invent unsupported command types.
- If the request cannot be handled, return an empty commands list
  and explain briefly in the message.
- For normal conversation or general questions, use an empty
  commands list and provide a helpful short message.
- Do not create commands the user did not request.
- For multiple requested actions, return multiple commands.
- Keep search queries and app names intact.
- Output valid JSON only.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=600
        )

        result = json.loads(
            response.choices[0].message.content
        )

        commands = result.get("commands", [])
        message = result.get("message", "")

        if not isinstance(commands, list):
            return [], "AI response format galat hai."

        # Allowlist: only commands supported by this application
        allowed_prefixes = (
            "open ",
            "close ",
            "play ",
            "search on google ",
            "search on youtube ",
            "search on amazon ",
            "search on flipkart ",
            "google search ",
            "youtube search ",
            "content ",
            "go to ",
            "system "
        )

        valid_system_commands = {
            "system volume up",
            "system volume down",
            "system mute",
            "system unmute",
            "system shutdown",
            "system restart",
            "system sleep",
            "system cancel shutdown"
        }

        safe_commands = []

        for item in commands:
            if not isinstance(item, str):
                continue

            item = item.strip()
            lowered = item.lower()

            if not item:
                continue

            if lowered.startswith("system "):
                if lowered in valid_system_commands:
                    safe_commands.append(lowered)
                continue

            if lowered.startswith(allowed_prefixes):
                # Require a value after the command prefix
                prefix = next(
                    (p for p in allowed_prefixes
                     if lowered.startswith(p)),
                    None
                )

                if prefix and item[len(prefix):].strip():
                    safe_commands.append(item)

        return safe_commands, message

    except Exception as e:
        print(f"[red]AI command generation error: {e}[/red]")
        return [], "AI command generate nahi kar paya."


# Asynchronous function to translate and execute user commands
async def TranslateAndExecute(commands):
    tasks = []
    for command in commands:
        cmd = command.lower().strip()
        if cmd.startswith("open "):
            tasks.append(asyncio.to_thread(OpenApp, cmd[5:]))
        elif cmd.startswith("close "):
            tasks.append(asyncio.to_thread(CloseApp, cmd[6:]))
        elif cmd.startswith("play "):
            tasks.append(asyncio.to_thread(PlayYoutube, cmd[5:]))
        elif cmd.startswith("content "):
            tasks.append(asyncio.to_thread(Content, cmd[8:]))
        elif cmd.startswith("google search "):
            tasks.append(asyncio.to_thread(GoogleSearch, cmd[14:]))
        elif cmd.startswith("search on google "):
            tasks.append(asyncio.to_thread(GoogleSearch, cmd[17:]))
        elif cmd.startswith("youtube search "):
            tasks.append(asyncio.to_thread(youtubeSearch, cmd[15:]))
        elif cmd.startswith("search on youtube "):
            tasks.append(asyncio.to_thread(youtubeSearch, cmd[18:]))
        elif cmd.startswith("search on amazon "):
            query = cmd[17:].strip()
            print(f"[OMNIS Automation] Searching {query} on Amazon")
            tasks.append(asyncio.to_thread(webbrowser.open_new_tab, f"https://www.amazon.in/s?k={requests.utils.quote(query)}"))
        elif cmd.startswith("search on flipkart "):
            query = cmd[19:].strip()
            print(f"[OMNIS Automation] Searching {query} on Flipkart")
            tasks.append(asyncio.to_thread(webbrowser.open_new_tab, f"https://www.flipkart.com/search?q={requests.utils.quote(query)}"))
        elif cmd.startswith("go to "):
            url = cmd[6:].strip()
            if not url.startswith("http"):
                url = "https://" + url
            print(f"[OMNIS Automation] Navigating to {url}")
            tasks.append(asyncio.to_thread(webbrowser.open_new_tab, url))
        elif cmd.startswith("volume "):
            tasks.append(asyncio.to_thread(System, cmd[7:]))
        elif cmd.startswith("system volume "):
            tasks.append(asyncio.to_thread(System, cmd[14:]))
        elif cmd.startswith("system "):
            tasks.append(asyncio.to_thread(System, cmd[7:]))
        else:
            print(f"No function found for: {command}")
    results = await asyncio.gather(*tasks)
    return results

# Main automation function
async def Automation(commands):
    if isinstance(commands, str):
        commands = [commands]

    final_commands = []
    allowed_prefixes = (
        "open ", "close ", "play ", "search on google ", "search on youtube ",
        "search on amazon ", "search on flipkart ", "google search ", "youtube search ",
        "content ", "go to ", "system ", "volume "
    )

    for cmd in commands:
        if not isinstance(cmd, str) or not cmd.strip():
            continue
        lowered = cmd.lower().strip()
        if not lowered.startswith(allowed_prefixes):
            safe_cmds, msg = GenerateCommands(cmd)
            if safe_cmds:
                if msg:
                    print(f"[OMNIS Automation] {msg}")
                final_commands.extend(safe_cmds)
            else:
                final_commands.append(cmd)
        else:
            final_commands.append(cmd)

    await TranslateAndExecute(final_commands)
    return True

if __name__ == "__main__":
    while True:
        user_input = input("Enter command (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        asyncio.run(Automation([user_input]))