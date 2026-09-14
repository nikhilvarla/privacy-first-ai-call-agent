from threading import Timer

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_engine import generate_ai_reply


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Privacy-First AI Call Agent",
    description="A privacy-first personal incoming-call AI assistant.",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------
# This allows your browser-based voice_test.html file
# to communicate with FastAPI during local development.
#
# This is suitable for local testing only.
# Later, restrict allow_origins to your real website domain.
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request and response models
# ---------------------------------------------------------

class MessageRequest(BaseModel):
    call_id: str
    message: str


class MessageResponse(BaseModel):
    call_id: str
    caller_message: str
    ai_reply: str


# ---------------------------------------------------------
# Temporary conversation storage
# ---------------------------------------------------------
# Each call gets its own conversation history.
#
# Example:
# {
#     "call-001": [
#         {"role": "user", "parts": [{"text": "Hello"}]},
#         {"role": "model", "parts": [{"text": "Hello, I am an AI assistant."}]}
#     ]
# }
#
# This is only temporary memory for local testing.
# It is not permanent database storage.
# ---------------------------------------------------------

conversation_histories: dict[str, list[dict]] = {}

# Stores cleanup timers for each call.
conversation_timers: dict[str, Timer] = {}

# Delete conversations after 10 minutes of inactivity.
CLEANUP_SECONDS = 600


# ---------------------------------------------------------
# Conversation cleanup functions
# ---------------------------------------------------------

def delete_call_history(call_id: str):
    """
    Delete one call's temporary conversation history.
    """

    conversation_histories.pop(call_id, None)

    timer = conversation_timers.pop(call_id, None)

    if timer is not None:
        timer.cancel()

    print(f"Temporary history deleted for {call_id}")


def schedule_cleanup(call_id: str):
    """
    Schedule deletion 10 minutes after the latest message.

    If the caller sends another message, the old timer is
    cancelled and a new 10-minute timer is started.
    """

    old_timer = conversation_timers.pop(call_id, None)

    if old_timer is not None:
        old_timer.cancel()

    new_timer = Timer(
        CLEANUP_SECONDS,
        delete_call_history,
        args=(call_id,),
    )

    # Do not keep the Python application alive only because
    # of this timer.
    new_timer.daemon = True

    conversation_timers[call_id] = new_timer
    new_timer.start()


# ---------------------------------------------------------
# Basic routes
# ---------------------------------------------------------

@app.get("/")
def home():
    """
    Basic home route.
    """

    return {
        "status": "online",
        "message": "Privacy-first AI call agent is running",
    }


@app.get("/health")
def health_check():
    """
    Health-check route.
    """

    return {
        "status": "healthy",
    }


# ---------------------------------------------------------
# Incoming call message route
# ---------------------------------------------------------

@app.post(
    "/incoming-call",
    response_model=MessageResponse,
)
def incoming_call(request: MessageRequest):
    """
    Receive a caller message and generate an AI reply.

    Every call_id gets its own temporary conversation history.
    """

    call_id = request.call_id.strip()
    caller_message = request.message.strip()

    if not call_id:
        return {
            "call_id": "",
            "caller_message": caller_message,
            "ai_reply": "A valid call ID is required.",
        }

    if not caller_message:
        return {
            "call_id": call_id,
            "caller_message": "",
            "ai_reply": "Sorry, I did not hear anything. Could you please repeat that?",
        }

    # Create a new conversation for a new call.
    if call_id not in conversation_histories:
        conversation_histories[call_id] = []

    conversation = conversation_histories[call_id]

    # Add the caller's message to the conversation.
    conversation.append(
        {
            "role": "user",
            "parts": [
                {
                    "text": caller_message,
                }
            ],
        }
    )

    try:
        # Generate the AI response using the complete conversation.
        ai_reply = generate_ai_reply(conversation)

    except Exception as error:
        print(f"AI error for {call_id}: {error}")

        ai_reply = (
            "Sorry, I am having trouble responding right now. "
            "Please try again later."
        )

    # Add the AI response to the conversation.
    conversation.append(
        {
            "role": "model",
            "parts": [
                {
                    "text": ai_reply,
                }
            ],
        }
    )

    # Reset the cleanup timer after every message.
    # The conversation will be deleted 10 minutes after
    # the latest message.
    schedule_cleanup(call_id)

    return {
        "call_id": call_id,
        "caller_message": caller_message,
        "ai_reply": ai_reply,
    }


# ---------------------------------------------------------
# End-call route
# ---------------------------------------------------------

@app.post("/end-call/{call_id}")
def end_call(call_id: str):
    """
    End a call immediately and delete its temporary history.
    """

    delete_call_history(call_id)

    return {
        "status": "call ended",
        "call_id": call_id,
        "message": "Temporary conversation history deleted",
    }


# ---------------------------------------------------------
# Manual reset route
# ---------------------------------------------------------

@app.post("/reset-conversation/{call_id}")
def reset_conversation(call_id: str):
    """
    Manually delete one call's temporary conversation.
    """

    delete_call_history(call_id)

    return {
        "status": "conversation reset",
        "call_id": call_id,
    }


# ---------------------------------------------------------
# Active calls route
# ---------------------------------------------------------

@app.get("/active-calls")
def active_calls():
    """
    Show currently stored temporary call IDs.

    This is only for local testing.
    """

    return {
        "active_call_ids": list(conversation_histories.keys()),
        "active_call_count": len(conversation_histories),
    }