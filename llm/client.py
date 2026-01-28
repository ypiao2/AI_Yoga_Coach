"""
LLM client supporting free/cheap providers: Groq, Google Gemini, Ollama.
Use one via LLM_PROVIDER + API key (or Ollama with no key).
"""
import os
import re
from typing import Iterator, Optional


def extract_json(text: str) -> str:
    """Extract JSON from LLM response (handles markdown code blocks)."""
    text = text.strip()
    # Try ```json ... ``` or ``` ... ```
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        return m.group(1).strip()
    # Otherwise use whole text
    return text


class LLMClient:
    """
    Unified LLM client for Groq (free tier), Gemini (free tier), or Ollama (local, free).
    """
    
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "")).lower()
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if self.provider == "groq" and (self.api_key or os.getenv("GROQ_API_KEY")):
            self._impl = "groq"
            self._key = self.api_key or os.getenv("GROQ_API_KEY")
        elif self.provider == "gemini" and (self.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
            self._impl = "gemini"
            self._key = self.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        elif self.provider == "ollama" or (not self.provider and not self.api_key):
            self._impl = "ollama"
            self._key = None
        else:
            # Auto-detect from keys
            if os.getenv("GROQ_API_KEY"):
                self._impl = "groq"
                self._key = os.getenv("GROQ_API_KEY")
            elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                self._impl = "gemini"
                self._key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            else:
                self._impl = "ollama"
                self._key = None

    @property
    def provider_name(self) -> str:
        """Provider id for status only (groq, gemini, ollama). No secrets."""
        return self._impl

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.5) -> str:
        """
        Send prompt to LLM and return raw text.
        """
        if self._impl == "groq":
            return self._groq(prompt, system_prompt, temperature)
        if self._impl == "gemini":
            return self._gemini(prompt, system_prompt, temperature)
        return self._ollama(prompt, system_prompt, temperature)

    def generate_stream(
        self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.5
    ) -> Iterator[str]:
        """
        Yield text chunks for streaming. Groq uses native streaming; Gemini/Ollama yield full text as one chunk.
        """
        if self._impl == "groq":
            yield from self._groq_stream(prompt, system_prompt, temperature)
        elif self._impl == "gemini":
            full = self._gemini(prompt, system_prompt, temperature)
            if full:
                yield full
        else:
            full = self._ollama(prompt, system_prompt, temperature)
            if full:
                yield full

    def _groq_stream(
        self, prompt: str, system_prompt: Optional[str], temperature: float
    ) -> Iterator[str]:
        try:
            from groq import Groq
            client = Groq(api_key=self._key)
            model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            msgs = []
            if system_prompt:
                msgs.append({"role": "system", "content": system_prompt})
            msgs.append({"role": "user", "content": prompt})
            stream = client.chat.completions.create(
                model=model,
                messages=msgs,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                part = (chunk.choices[0].delta.content or "") if chunk.choices else ""
                if part:
                    yield part
        except Exception as e:
            raise RuntimeError(f"Groq error: {e}") from e

    def _groq(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        try:
            from groq import Groq
            client = Groq(api_key=self._key)
            model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            msgs = []
            if system_prompt:
                msgs.append({"role": "system", "content": system_prompt})
            msgs.append({"role": "user", "content": prompt})
            r = client.chat.completions.create(
                model=model,
                messages=msgs,
                temperature=temperature,
            )
            return (r.choices[0].message.content or "").strip()
        except Exception as e:
            raise RuntimeError(f"Groq error: {e}") from e
    
    def _gemini(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            model = genai.GenerativeModel(model_name)
            full = (system_prompt or "") + "\n\n" + prompt if system_prompt else prompt
            r = model.generate_content(full, generation_config={"temperature": temperature})
            return (getattr(r, "text", None) or "").strip()
        except Exception as e:
            raise RuntimeError(f"Gemini error: {e}") from e
    
    def _ollama(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        try:
            import requests
            url = os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/chat"
            model = os.getenv("OLLAMA_MODEL", "llama3.2")
            msgs = []
            if system_prompt:
                msgs.append({"role": "system", "content": system_prompt})
            msgs.append({"role": "user", "content": prompt})
            r = requests.post(
                url,
                json={"model": model, "messages": msgs, "stream": False, "options": {"temperature": temperature}},
                timeout=120,
            )
            r.raise_for_status()
            out = r.json().get("message", {}).get("content", "")
            return (out or "").strip()
        except Exception as e:
            raise RuntimeError(f"Ollama error: {e}. Is Ollama running? Try: ollama run llama3.2") from e


def create_llm_client(provider: Optional[str] = None, api_key: Optional[str] = None) -> Optional[LLMClient]:
    """
    Create an LLM client if any provider is configured.
    Returns None if no key/provider set (use rule-based fallback).
    """
    p = (provider or os.getenv("LLM_PROVIDER", "")).lower()
    if p == "ollama":
        return LLMClient(provider="ollama")
    if p == "groq" and (api_key or os.getenv("GROQ_API_KEY")):
        return LLMClient(provider="groq", api_key=api_key)
    if p == "gemini" and (api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return LLMClient(provider="gemini", api_key=api_key)
    # Auto-detect from keys (ignore provider if another key is set)
    if os.getenv("GROQ_API_KEY"):
        return LLMClient(provider="groq")
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return LLMClient(provider="gemini")
    if p == "ollama" or os.getenv("OLLAMA_URL"):
        return LLMClient(provider="ollama")
    return None
