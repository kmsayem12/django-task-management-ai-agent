from langchain_google_genai import ChatGoogleGenerativeAI

from django.conf import settings

GOOGLE_API_KEY = settings.GOOGLE_API_KEY
GOOGLE_AI_MODEL = settings.GOOGLE_AI_MODEL


def init_llm():
    return ChatGoogleGenerativeAI(
        model=settings.GOOGLE_AI_MODEL,
        api_key=settings.GOOGLE_API_KEY,
        temperature=0.0,
        max_retries=2
    )
