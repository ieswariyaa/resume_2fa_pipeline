from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str
    ALGORITHM:str='HS256'
    ACCESS_TOKEN_MINUTES:int=60
    OTP_EXPIRE_MINUTES:int=5
    SMTP_HOST:str=''
    SMTP_PORT:int=587
    SMTP_USER:str=''
    SMTP_PASSWORD:str=''

    class Config:
        env_file='.env'

settings=Settings()