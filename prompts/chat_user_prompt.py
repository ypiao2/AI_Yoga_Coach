"""
Chat user prompt template for the yoga Q&A chatbot.
Placeholders: context, user_message
"""

CHAT_USER_PROMPT_TEMPLATE = """Relevant yoga knowledge (use when it helps):
{context}

---
User question: {user_message}

Answer in well-structured Markdown:
"""
