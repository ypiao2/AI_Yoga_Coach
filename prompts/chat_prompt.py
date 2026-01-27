"""
Chat prompts for the yoga Q&A chatbot.
Imports system and user templates from sibling modules.
"""
from .chat_system_prompt import CHAT_SYSTEM_PROMPT
from .chat_user_prompt import CHAT_USER_PROMPT_TEMPLATE


def format_chat_user_prompt(context: str, user_message: str) -> str:
    """Format the chat user prompt with RAG context and the user's question."""
    return CHAT_USER_PROMPT_TEMPLATE.format(context=context, user_message=user_message)
