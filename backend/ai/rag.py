from abc import ABC , abstractmethod

class RagMini(ABC):
    retriever : str 
    description : str 
        
    @abstractmethod
    def get_document_relevant(self , query : str) -> str:
        raise NotImplementedError("Bạn phải override hàm get_document_relevant()")
    
    @abstractmethod
    def invoke(self , messages : str) -> str : 
        raise NotImplementedError("Bạn phải override hàm invoke()")
        
    
    
    
        
    
    
    
        
    
    
    