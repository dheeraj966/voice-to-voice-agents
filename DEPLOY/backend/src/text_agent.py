"""
Simple text-only agent using local Ollama.
This bypasses STT/TTS requirements for testing the LLM connection.
"""
import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env.local")

# Local Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

SYSTEM_PROMPT = """You are a helpful voice AI assistant. 
You eagerly assist users with their questions by providing information from your extensive knowledge.
Your responses are concise, to the point, and without any complex formatting.
You are curious, friendly, and have a sense of humor."""

def main():
    print("=" * 50)
    print("Local Ollama Chat Agent")
    print(f"Model: {OLLAMA_MODEL}")
    print(f"URL: {OLLAMA_BASE_URL}")
    print("=" * 50)
    print("Type 'quit' to exit\n")
    
    # Create OpenAI client pointing to Ollama
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama"  # Ollama doesn't need a real key
    )
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            if not user_input:
                continue
                
            messages.append({"role": "user", "content": user_input})
            
            print("\nAssistant: ", end="", flush=True)
            
            # Stream the response
            response = client.chat.completions.create(
                model=OLLAMA_MODEL,
                messages=messages,
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print()  # New line after response
            messages.append({"role": "assistant", "content": full_response})
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
