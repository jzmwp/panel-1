from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    database_url: str = "sqlite:///./data/panel1.db"
    upload_dir: str = "./uploads"
    log_level: str = "INFO"
    supabase_url: str = ""
    supabase_anon_key: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")


settings = Settings()
