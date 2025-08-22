import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.vectorstores import VectorStoreRetriever
from ai.config.config import embeddings, VECTORSTORE_PATH, DATA_PATH
from ai.data_loader import data_loader

class Retriever:
    def __init__(self, name, data_level="folder"):
        self.vectorstore_path = VECTORSTORE_PATH[name]
        self.data_path = DATA_PATH[name]
        self.data_level = data_level

        self.vectorstore = None
        self.retriever = None

        # Kiểm tra xem vectorstore đã tồn tại chưa
        if os.path.exists(os.path.join(self.vectorstore_path, "index.faiss")):
            print("Vectorstore exists. Loading...")
            self.load()
        else:
            print("Vectorstore does not exist. Building...")
            self.build()

    def build(self):
        # Load documents
        if self.data_level == "folder":
            documents = data_loader.load_folder(self.data_path)
        elif self.data_level == "multi_folders":
            documents = data_loader.load_dir(self.data_path)

        if len(documents) == 0:
            raise ValueError(f"No documents found in {self.data_path}")

        # Khởi tạo FAISS index với đúng dimension của embeddings
        index = faiss.IndexFlatL2(384)
        vectorstore = FAISS(
            embedding_function=embeddings,
            index=index,
            index_to_docstore_id={},
            docstore=InMemoryDocstore()
        )

        # Thêm documents vào vectorstore
        vectorstore.add_documents(documents)
        vectorstore.save_local(self.vectorstore_path)

        self.vectorstore = vectorstore
        self.retriever = VectorStoreRetriever(vectorstore=vectorstore)

    def load(self):
        vectorstore = FAISS.load_local(
            folder_path=self.vectorstore_path,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        self.vectorstore = vectorstore
        self.retriever = VectorStoreRetriever(vectorstore=vectorstore)


## Test
if __name__ == "__main__":
    a = Retriever(name="QuyDinh")
    query = "Điện nước ở ký túc xá như nào"

    answer = a.retriever.get_relevant_documents(query=query)
    for i, doc in enumerate(answer):
        print(f"--- Document {i} ---")
        print(doc.page_content)
        print(doc.metadata)
