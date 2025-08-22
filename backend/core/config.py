from pydantic_settings import BaseSettings 

class Settings(BaseSettings):
  DATABASE_URL : str 
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
  GROQ_API_KEY : str 
  HF_TOKEN : str 
  
  SECRET_KEY : str 
  GROQ_API_KEY : str 
  class Config : 
    env_file = ".env"
    
settings = Settings()