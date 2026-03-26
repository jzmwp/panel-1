from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    database_url: str = "sqlite:///./data/panel1.db"
    upload_dir: str = "./uploads"
    log_level: str = "INFO"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Strip whitespace from env var values
        object.__setattr__(self, 'log_level', self.log_level.strip())
        object.__setattr__(self, 'database_url', self.database_url.strip())
        object.__setattr__(self, 'anthropic_api_key', self.anthropic_api_key.strip())
    supabase_url: str = ""
    supabase_anon_key: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")


settings = Settings()
