"""
LLM factory — routes to the correct provider based on model name prefix.
Groq: llama-*, mixtral-* 
Gemini: gemini-*

All agents import get_llm() from here instead of instantiating
ChatGroq or ChatGoogleGenerativeAI directly. Provider switching
happens in config.py only — change model names there, nothing else.
"""
from config import GROQ_API_KEY, GEMINI_API_KEY


def get_llm(model: str, temperature: float = 0.0):
    if model.startswith("gemini"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=GEMINI_API_KEY,
            temperature=temperature
        )
    else:
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=temperature
        )


def get_groq_client():
    """
    Raw Groq SDK client for tool-calling — LangChain's ChatGroq wrapper
    doesn't expose native tool_choice='required' the same way. Only used
    by the agentic critic loop; everything else keeps using get_llm().
    """
    from groq import Groq
    from config import GROQ_API_KEY
    return Groq(api_key=GROQ_API_KEY)