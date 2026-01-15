"""Configuration management for the Content Agent System."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Project paths
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = project_root / "data"
    output_dir: Path = data_dir / "outputs"
    sample_inputs_dir: Path = data_dir / "sample_inputs"

    # API Keys
    google_api_key: str = ""
    mem0_api_key: Optional[str] = None
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    news_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Application settings
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = True

    # Database
    database_url: Optional[str] = None
    redis_url: Optional[str] = None

    # Gemini Configuration
    gemini_model_pro: str = "gemini-1.5-pro-latest"
    gemini_model_flash: str = "gemini-1.5-flash-latest"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 8192

    # Agent Configuration
    max_agents_parallel: int = 3
    agent_timeout_seconds: int = 300

    # Content Generation Settings
    default_case_study_length: int = 1200  # words
    default_white_paper_length: int = 3000  # words
    max_personas_per_generation: int = 50

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sample_inputs_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
