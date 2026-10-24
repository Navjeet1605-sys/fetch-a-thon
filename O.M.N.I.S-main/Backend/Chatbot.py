import os
import datetime
from dotenv import dotenv_values
from groq import Groq

# Setup Base directory and load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_vars = dotenv_values(os.path.join(BASE_DIR, ".env"))

Username = "Navjeet"
Assistantname = "OMNIS"

groq_key = os.environ.get("GroqAPIKey") or env_vars.get("GroqAPIKey")
client = Groq(api_key=groq_key) if groq_key else None

# In-memory chat history (no disk chat log)
messages = []

# Define system message
System = (
    "Hello, I am Navjeet, You are a very accurate and advanced AI chatbot named OMNIS which also has real-time up-to-date information from the internet.\n"
    "*** Do not tell time until I ask, do not talk too much, just answer the question.***\n"
    "*** Reply in only English, even if the question is in Hindi, reply in English.***\n"
    "*** Do not provide notes in the output, just answer the question and never mention your training data. ***"
)

SystemChatBot = [
    {"role": "system", "content": System}
]


def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes :{second} seconds.\n"
    return data


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)


def ChatBot(Query):
    global messages
    if not client:
        return "Groq client is not initialized. Please verify your GroqAPIKey in .env."

    try:
        messages.append({"role": "user", "content": f"{Query}"})

        # Keep context reasonable (last 10 messages)
        recent_messages = messages[-10:]

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + recent_messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "").strip()
        messages.append({"role": "assistant", "content": Answer})
        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"ChatBot error: {e}")
        return "I encountered an issue processing your request."


if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))