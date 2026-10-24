import sys
from .client import query_finance_agent

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    print("=" * 60)
    print(" 📈 O.M.N.I.S Crypto & Finance Agent (Agentverse)")
    print("=" * 60)
    print("Type your financial or crypto question below.")
    print("Examples:")
    print("  - 'What is Bitcoin price?'")
    print("  - 'What is Fetch.ai price?'")
    print("  - 'What causes inflation?'")
    print("  - 'Explain market capitalization'")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            q = input("\n[OMNIS Finance Agent] Ask >>> ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit", "q"]:
                print("Exiting Finance Agent. Have a great day!")
                break
            
            print("\nThinking & Fetching live data...")
            answer = query_finance_agent(q)
            print(f"\nResponse:\n{answer}")
        except KeyboardInterrupt:
            print("\nSession ended.")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
