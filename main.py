import os
from dotenv import load_dotenv
from llm_client import GeminiProvider, OllamaProvider, LLMClient
from mongo_logger import MongoLogger

load_dotenv()

print("=" * 36)
print("       WEEK 3: LLM MONITORING")
print("=" * 36)
print("1. Gemini")
print("2. Ollama")
choice = input("Select provider (1/2): ").strip()

logger = None
try:
    # MongoDB must be installed and its service must be running.
    logger = MongoLogger()

    if choice == "1":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Add GEMINI_API_KEY to .env to use Gemini.")
        provider = GeminiProvider(api_key)
    elif choice == "2":
        provider = OllamaProvider(os.getenv("OLLAMA_MODEL", "llama3.2"))
    else:
        raise ValueError("Invalid selection. Choose 1 or 2.")

    client = LLMClient(provider, logger)
    prompt = input("Enter your question: ").strip()
    if not prompt:
        raise ValueError("The prompt cannot be empty.")

    answer = client.generate(prompt)
    print("\n========== AI RESPONSE ==========\n")
    print(answer)
    print("\n========== COMPLETED ==========")

except Exception as error:
    print("\nApplication error:", error)
    print("Check that Ollama and MongoDB are running, and that the selected model exists.")
finally:
    if logger is not None:
        logger.close()
