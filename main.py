from fastapi import FastAPI, Response
from twilio.twiml.voice_response import VoiceResponse

app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "running",
        "project": "Privacy-first AI Call Agent"
    }


@app.post("/incoming-call")
async def incoming_call():
    response = VoiceResponse()

    response.say(
        "Hi, you are speaking with Nikhil's AI assistant. "
        "I am an AI, not Nikhil himself. "
        "Please do not share passwords, OTPs, banking details, "
        "PINs, or other sensitive information. "
        "How may I help you?",
        voice="alice",
        language="en-IN"
    )

    response.pause(length=2)

    response.say(
        "Thank you. The AI conversation system is currently being tested.",
        voice="alice",
        language="en-IN"
    )

    return Response(
        content=str(response),
        media_type="application/xml"
    )