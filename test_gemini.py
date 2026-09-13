import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)

instructions = """
You are JARVIS, a personal AI assistant.

PERSONALITY:
- Calm
- Professional
- Helpful
- Intelligent
- Clear
- Concise

BEHAVIOR:
- Understand what the user is asking.
- Give accurate and useful answers.
- Explain difficult concepts simply.
- Ask for clarification when necessary.

RULES:
- Never claim an action was performed when it was not.
- Never pretend to have access to something you cannot access.
- Do not invent information.
- Ask for confirmation before potentially destructive actions.

Your purpose is to help the user accomplish tasks safely and efficiently.
"""

chat = client.chats.create(
    model="gemini-3.1-flash-lite",
    config={
        "system_instruction": instructions
    }
)

print("JARVIS: Online. How may I assist you?")

while True:

    user_input = input("\nYou: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        print("JARVIS: Goodbye.")
        break

    if not user_input:
        continue

    try:

        response = chat.send_message_stream(user_input)

        print("JARVIS: ", end="")

        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)

        print()

    except Exception as error:

        print(
            "\nJARVIS: I'm unable to complete that request right now."
        )

        print("Developer information:", error)