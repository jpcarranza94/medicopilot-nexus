"""
Configuration settings for MediCopilot Nexus backend
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Saptiva API Configuration
    SAPTIVA_API_KEY: str = os.getenv("SAPTIVA_API_KEY", "")
    SAPTIVA_BASE_URL: str = "https://api.saptiva.com"

    # Model Configuration
    SAPTIVA_FAST_MODEL: str = "Saptiva Legacy"  # For real-time suggestions
    SAPTIVA_OPS_MODEL: str = "Saptiva Ops"      # For clinical decision-making

    # API Configuration
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "MediCopilot Nexus"
    VERSION: str = "0.1.0"

    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3003",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3003",
    ]

    # Weaviate Configuration (for RAG - optional for MVP)
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "")
    WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY", "")

    # LLM Parameters
    TEMPERATURE: float = 0.3  # Lower for medical accuracy
    MAX_TOKENS: int = 6000  # Doubled for complete responses

    # Timeouts
    LLM_TIMEOUT: int = 30  # seconds


settings = Settings()
