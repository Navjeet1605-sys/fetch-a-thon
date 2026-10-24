import os
import sys
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration
Username = "Navjeet"
Assistantname = "OMNIS"
GroqAPIKey = env_vars.get("GroqAPIKey")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
# Initialize the Groq client with the provided API key if present.
client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# System Prompt me thoda aur clear instruction de diya hai
System = (
    "Hello, I am Navjeet, You are a very accurate and advanced AI chatbot named OMNIS which has real-time up-to-date information from the internet.\n"
    "*** Provide Answers In a Professional, very short and direct way. ***\n"
    "*** Avoid extra conversational filler or website links. Just give the exact factual answer or price from the provided data. ***"
)

messages = []

# 2. Free, Fast aur Stable Search Engine Function using ddgs
# Updated GoogleSearch Function with Smart Query Injection
def GoogleSearch(query):
    # Agar query me gold, bitcoin ya price jaise words hain, toh query ko optimize karo
    optimized_query = query
    lower_query = query.lower()
    
    if "gold" in lower_query or "price" in lower_query or "rate" in lower_query:
        if "today" not in lower_query:
            optimized_query += " live price today in INR"
            
    Answer = f"The search results for '{optimized_query}' are:\n[start]\n"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(optimized_query, max_results=5)
            if results:
                for item in results:
                    Answer += f"Title: {item['title']}\nDescription: {item['body']}\n\n"
            else:
                Answer += "No results found on the internet.\n"
    except Exception as e:
        Answer += f"Search Error: {e}\n"
        
    Answer += "[end]"
    return Answer


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds. \n"
    return data

def RealtimeSearchEngine(prompt):
    # Delegate to the standalone WebSearchAgent
    try:
        from Agents.WebSearchAgent import query_web_search
        return query_web_search(prompt)
    except Exception as e:
        print(f"[WebSearchAgent] Falling back to default search: {e}")

    # Fallback to direct search if import fails
    return AnswerModifier(GoogleSearch(prompt))


if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
