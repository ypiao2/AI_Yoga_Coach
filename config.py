"""
Configuration file for AI Yoga Coach
"""
import os
from typing import Optional


class Config:
    """Application configuration"""
    
    # Database Configuration
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")  # sqlite, mongodb, supabase
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "yoga_coach.db")
    MONGODB_URI: Optional[str] = os.getenv("MONGODB_URI")
    
    # API Keys (set via environment variables)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    # Supabase Configuration (optional, paid)
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # LLM Configuration (free/cheap: groq, gemini, ollama)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")  # groq | gemini | ollama
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.5"))
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    # Koyeb/ai-builders.space set PORT at runtime; fallback for local dev
    API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    
    # RAG Settings
    RAG_ENABLED: bool = os.getenv("RAG_ENABLED", "True").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        # For v1.0, database and LLM keys are optional
        # SQLite works out of the box with no configuration
        return True
