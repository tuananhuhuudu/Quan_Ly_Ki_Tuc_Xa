from passlib.context import CryptContext 

pwd_context = CryptContext(schemes=["bcrypt"] , deprecated = "auto")

def verify_password(password_input : str , password_in_db : str):
  return pwd_context.verify(password_input , password_in_db)

def hash_password(password_input : str):
  return pwd_context.hash(password_input)

