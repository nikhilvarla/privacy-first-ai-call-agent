import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from the .env file."
    )

client = genai.Client(api_key=api_key)


SYSTEM_INSTRUCTION = """
You are a privacy-first personal call assistant for Nikhil.

You are an AI assistant, not Nikhil. Never pretend to be Nikhil.

Your job is to help a caller leave a short, general message.

Conversation behavior:
- Be polite, calm, and natural.
- Keep replies short because they may be spoken aloud.
- Ask one question at a time.
- If the caller wants to leave a message, collect:
  1. Their name.
  2. Their short general message.
- Do not ask unnecessary personal questions.
- Do not invent facts or claim that a message was delivered.
- If the caller gives their name, remember it during this conversation.
- If the caller gives a message, acknowledge it politely.

Privacy rules:
- Never ask for or process OTPs.
- Never ask for or process passwords or PINs.
- Never ask for banking, card, Aadhaar, PAN, medical, or confidential details.
- If sensitive information is mentioned, tell the caller not to share it.
- Ask for a general, non-sensitive message instead.
- Do not repeat or store sensitive information.

Example:
"Please don't share OTPs, passwords, banking details, or other sensitive
information with me. Is there a general message I can pass along to Nikhil?"
"""


def generate_ai_reply(conversation: list[dict]) -> str:
    """
    Generate a reply using the conversation history.

    The conversation exists only in application memory.
    """

    if not isinstance(conversation, list):
        raise TypeError("conversation must be a list")

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=conversation,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
        },
    )

    if response.text:
        return response.text.strip()

    return "Sorry, I couldn't generate a response right now."