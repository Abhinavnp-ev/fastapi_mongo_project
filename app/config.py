from pydantic_settings  import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    DATABASE_NAME: str
    GCS_BUCKET_NAME: str
    GCS_CREDENTIALS_PATH: str = "credentials.json"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
