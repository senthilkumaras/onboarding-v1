import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from langchain_groq import ChatGroq

CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "llama-3.1-70b-versatile")
FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "llama-3.1-8b-instant")


def get_intent_llm():
    # Cheap + fast for classification/routing
    return ChatGroq(model=FAST_MODEL, temperature=0)


def get_voice_llm(topic: str):
    # Friendly tone for onboarding
    return ChatGroq(model=CHAT_MODEL, temperature=0.6)


def get_policy_llm():
    # Grounded answers (RAG). Keep temperature low.
    return ChatGroq(model=CHAT_MODEL, temperature=0)
