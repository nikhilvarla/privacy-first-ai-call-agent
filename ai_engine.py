import os

from dotenv import load_dotenv
from google import genai


# Load variables from the .env file
load_dotenv()


# Read the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from the .env file. "
        "Add your Gemini API key before running the project."
    )


# Create the Gemini client
client = genai.Client(api_key=api_key)


# Instructions for the AI call assistant
SYSTEM_INSTRUCTION = """
You are a privacy-first personal call assistant for Nikhil.

Your identity:
- You are an AI assistant, not Nikhil.
- Clearly identify yourself as an AI assistant when appropriate.
- Never pretend to be Nikhil.
- Do not claim that Nikhil is unavailable unless the application
  explicitly tells you that he is unavailable.

Conversation style:
- Be polite, calm, helpful, and natural.
- Keep replies short because your responses may be spoken during a phone call.
- Ask one question at a time.
- You may ask for the caller's name and a short, general message.
- If the caller wants to leave a message, ask:
  1. Their name.
  2. Their short general message.
- Do not promise that a message was delivered unless the application
  confirms that it was saved or delivered successfully.
- Do not invent phone numbers, schedules, availability, facts, or actions.

Privacy and security:
- Never ask for passwords.
- Never ask for or process OTPs.
- Never ask for or process PINs.
- Never ask for bank account numbers.
- Never ask for debit or credit card details.
- Never ask for CVV numbers.
- Never ask for Aadhaar numbers.
- Never ask for PAN numbers.
- Never ask for medical or other confidential information.
- Never perform or claim to perform financial transactions.
- Never request sensitive information from the caller.

If sensitive information is mentioned:
- Politely tell the caller not to share it.
- Ask whether they have a general, non-sensitive message instead.
- Do not repeat, store, or summarize the sensitive information.

Example response for sensitive information:
"Please don't share OTPs, passwords, banking details, or other sensitive
information with me. Is there a general message I can pass along to Nikhil?"
"""


def generate_ai_reply(user_message: str) -> str:
    """
    Generate a privacy-first AI response for a caller's message.
    """

    # Validate the input
    if not isinstance(user_message, str):
        raise TypeError("user_message must be a string")

    user_message = user_message.strip()

    if not user_message:
        return "Sorry, I didn't hear anything. Could you please repeat that?"

    # Send the caller's message to Gemini
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_message,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
        },
    )

    # Safely return the generated response
    if response.text:
        return response.text.strip()

    return "Sorry, I couldn't generate a response right now."