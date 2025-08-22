import os 

from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_groq import ChatGroq 

from dotenv import load_dotenv 
load_dotenv()

os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="Gemma2-9b-It"
)

print(os.getcwd())
data_path = os.path.join(os.getcwd() , "ai" , "ragg" , "data")

VECTORSTORE_PATH =  {
    "CCCD" : os.path.join(data_path , "vectorstore" , "CCCD"),
    "QuyDinh" : os.path.join(data_path , "vectorstore" , "QuyDinh")
}
DATA_PATH = {
    "CCCD" : os.path.join(data_path , "data_txt" , "CCCD_Guide"),
    "QuyDinh" : os.path.join(data_path , "data_txt" , "QuyDinh")
}
print("Exists:", os.path.exists(DATA_PATH["CCCD"]))