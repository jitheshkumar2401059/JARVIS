import os
from dotenv import load_dotenv
from google import genai


load_dotenv()


class GeminiBrain:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY was not found. "
                "Check your .env file."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.instructions = """
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

        self.chat = self.client.chats.create(
            model="gemini-3.1-flash-lite",
            config={
                "system_instruction": self.instructions
            }
        )

    def ask(self, user_input):

        return self.chat.send_message_stream(
            user_input
        )