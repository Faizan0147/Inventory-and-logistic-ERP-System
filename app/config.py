from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # SMTP settings for sending login credentials via email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "umerfaisal132@gmail.com"
    

    # Ngrok settings 
    NGROK_AUTHTOKEN: str = ""
    NGROK_DOMAIN: str = ""  
    
    
    # Groq settings
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Tool call control
    TOOL_CALL_MAX_STEPS: int = 30
    

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
