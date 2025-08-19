from pydantic_settings import BaseSettings 

class Settings(BaseException):
  DATABASE_URL : str 
  GROG_API_KEY : str 
  class Config : 
    env_file = ".env"
    
settings = Settings()