from ai_engine import generate_ai_reply


test_messages = [
    "Hello, who are you?",
    "Can you take a message for Nikhil?",
    "Please tell Nikhil to call me back.",
    "What is your phone number?",
    "My OTP is 123456. Can you tell Nikhil?",
    "My bank account number is 123456789.",
]


for message in test_messages:
    print("\nCaller:", message)
    print("AI:", generate_ai_reply(message))