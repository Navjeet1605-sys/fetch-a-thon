import os
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation, GenerateCommands, TranslateAndExecute
from Backend.Chatbot import ChatBot
from Agents.FinanceAgent import query_finance_agent
import asyncio
from time import sleep
from rich import print
import subprocess
import json
import sys

Username = "Navjeet"
Assistantname = "OMNIS"
DefaultMessage = '''Navjeet : Hello OMNIS, How are you?
OMNIS : Welcome Navjeet. I am doing well. How may i help you?'''
subprocesses = []
Functions = ["open", "close", "play", "volume","content", "google search", "youtube search", "search on google", "search on youtube"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def MainExecution(query_input: str = None):

    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    if query_input:
        Query = query_input.strip()
    else:
        try:
            Query = input("\n[OMNIS Input (Text)] >>> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting O.M.N.I.S. Goodbye!")
            sys.exit(0)

    if not Query or not Query.strip():
        return False

    # Output query in explicit text format
    print("\n" + "=" * 50)
    print(f"User Query (Text) : {Query}")
    print("=" * 50)

    Decision = FirstLayerDMM(Query)
    print(f"Routing Decision  : {Decision}\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            print("OK, please wait. Image is generating...")
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            asyncio.run(Automation(Decision))
            TaskExecution = True

    if ImageExecution == True:
        with open(r"ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(
                ['python', r'Backend/ImageGeneration.py'], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=True
            )
            subprocesses.append(p1)
            p1.wait()  # Ensures the subprocess completes before continuing
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
            if p1.stderr:
                print("Full error output:", p1.stderr.read().decode())

    if G and R:
        Answer = RealtimeSearchEngine(Mearged_query)
        print(f"\n--------------------------------------------------")
        print(f"User Query : {Query}")
        print(f"OMNIS      : {Answer}")
        print(f"--------------------------------------------------\n")
        return Answer

    else:
        for Queries in Decision:

            if "general" in Queries:
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryFinal)
                print(f"\n--------------------------------------------------")
                print(f"User Query : {Query}")
                print(f"OMNIS      : {Answer}")
                print(f"--------------------------------------------------\n")
                return Answer

            elif "finance" in Queries:
                QueryFinal = Queries.replace("finance ", "")
                Answer = query_finance_agent(QueryFinal)
                print(f"\n--------------------------------------------------")
                print(f"User Query : {Query}")
                print(f"OMNIS      : {Answer}")
                print(f"--------------------------------------------------\n")
                return Answer

            elif "realtime" in Queries:
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryFinal)
                print(f"\n--------------------------------------------------")
                print(f"User Query : {Query}")
                print(f"OMNIS      : {Answer}")
                print(f"--------------------------------------------------\n")
                return Answer

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryFinal)
                print(f"\n--------------------------------------------------")
                print(f"User Query : {Query}")
                print(f"OMNIS      : {Answer}")
                print(f"--------------------------------------------------\n")
                sys.exit(0)

    if TaskExecution:
        print(f"\n--------------------------------------------------")
        print(f"User Query : {Query}")
        print(f"OMNIS      : Automation task completed successfully.")
        print(f"--------------------------------------------------\n")
        return True

    if ImageExecution:
        print(f"\n--------------------------------------------------")
        print(f"User Query : {Query}")
        print(f"OMNIS      : Image generation initiated for '{ImageGenerationQuery}'.")
        print(f"--------------------------------------------------\n")
        return True

    # Fallback if no specific condition triggered
    Answer = ChatBot(Query)
    print(f"\n--------------------------------------------------")
    print(f"User Query : {Query}")
    print(f"OMNIS      : {Answer}")
    print(f"--------------------------------------------------\n")
    return Answer


# =========================
# MAIN ENTRY POINT
# =========================

async def Main():
    print("\n[bold cyan]O.M.N.I.S AI is Ready![/bold cyan]")
    print("[yellow]Hindi, Hinglish ya English mein prompt likhein.[/yellow]")
    print("[white]Exit ke liye 'exit' type karein.[/white]")

    while True:
        try:
            prompt = await asyncio.to_thread(
                input, "\n[You] Enter prompt: "
            )

            prompt = prompt.strip()

            if prompt.lower() in ("exit", "quit"):
                print("[cyan]O.M.N.I.S stopped.[/cyan]")
                break

            if not prompt:
                continue

            print("[cyan]AI is understanding your prompt...[/cyan]")

            commands, message = await asyncio.to_thread(
                GenerateCommands, prompt
            )

            if message:
                print(f"[blue]AI: {message}[/blue]")

            if not commands:
                # If no system/automation commands, process through OMNIS AI Agents & Knowledge Engine
                await asyncio.to_thread(MainExecution, prompt)
                continue

            print("\n[bold green]Executing Commands:[/bold green]")

            for index, command in enumerate(commands, start=1):
                print(f"{index}. {command}")

            await TranslateAndExecute(commands)

        except KeyboardInterrupt:
            print("\n[yellow]O.M.N.I.S stopped.[/yellow]")
            break

        except Exception as e:
            print(f"[red]Main error: {e}[/red]")


if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    asyncio.run(Main())