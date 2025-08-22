import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from ai.config.config import (
    llm , 
    embeddings
)


# Prompt template đơn giản
def prompt_template(task):
    if task == "search_information":
        prompt_system = (
            """
            Bạn là một trợ lý ảo quản lý ký túc xá.
            Nhiệm vụ của bạn: trả lời câu hỏi của sinh viên dựa trên dữ liệu cung cấp (context).
            
            Quy tắc:
            - Trả lời ngắn gọn, rõ ràng, dễ hiểu.
            - Nếu có quy định hoặc hướng dẫn, hãy liệt kê từng bước hoặc nêu rõ nội dung.
            - Nếu không có thông tin trong dữ liệu thì trả lời:
              "Xin lỗi, hiện tại tôi chưa có thông tin để trả lời câu hỏi này."
            """
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_system),
                ("system", "Thông tin:\n{context}"),
                ("human", "{input}")
            ]
        )
    else:
        prompt_template = ChatPromptTemplate.from_template(
            """
            Bạn là trợ lý ảo ký túc xá.
            Hãy chọn function phù hợp nhất để xử lý câu hỏi của sinh viên.

            Các function có sẵn:
            {tool_description}

            Câu hỏi:
            {question}

            Quy tắc:
            - Chỉ trả về tên function.
            - Nếu không liên quan, trả lời:
              "Thông tin này chưa có."
            """
        )
    return prompt_template


def chat_llm_with_ragg(task: str, params={}):
    prompt = prompt_template(task)
    formatted_messages = prompt.format_messages(**params)
    response = llm.invoke(formatted_messages)
    return response.content


if __name__ == "__main__":
    response = chat_llm_with_ragg(
        task="search_information",
        params={
            "context": """
                Nội quy KTX:
                - Mở cổng: 05h30, đóng cổng: 23h00.
                - Khách phải đăng ký tại cổng, không được ngủ lại qua đêm.
                - Cấm nuôi thú cưng, đun nấu trong phòng.
            """,
            "input": "Khách có được ngủ lại không?"
        }
    )
    
    print("Assistant:", response)
