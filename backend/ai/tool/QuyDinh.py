import os 
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".." , "..")))
from ai.rag import RagMini
from ai.retriever.retriever import Retriever
from ai.llm.models import chat_llm_with_ragg

name = "QuyDinh"

class QuyDinh(RagMini):
    def __init__(self):
        self.retriever = Retriever(name)
        self.description = "Cung cấp các nội quy của kí túc xá"
        
    def get_document_relevant(self, query):
        docs = self.retriever.retriever.invoke(
            query
        )
        
        return "\n".join([doc.page_content for doc in docs])
    
    def invoke(self , question : str) -> str : 
        context = self.get_document_relevant(question)
        response = chat_llm_with_ragg( 
            task = "search_information",
            params = {"input" : question , "context" : context}
        )
        
        return response

QuyDinh_RAGG = QuyDinh()

if __name__ == "__main__":
    question = "Quy định về sử dụng nước trong KTX?"
    result = QuyDinh_RAGG.invoke(question)
    print("Câu hỏi:", question)
    print("Trợ lý trả lời:", result)