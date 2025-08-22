import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from ai.tool import QuyDinh

from ai.llm.models import chat_llm_with_ragg

from ai.config.config import (
    llm
)
tools = {
    "QuyDinh": QuyDinh.QuyDinh_RAGG  
}

class ToolSelector:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.tool_description = "\n".join(
            [f"{name}: {obj.description}" for name, obj in tools.items()]
        )
        self.current_function = None

    def check_same_function(self, question):
        prompt = ChatPromptTemplate.from_template("""
        Function hiện tại: {function_name}
        Câu hỏi mới: {question}
        Câu hỏi này:
        - A. Liên quan đến function hiện tại
        - B. Chủ đề mới, cần chọn function khác
        Trả lời chỉ A hoặc B.
        """)
        messages = prompt.format_messages(
            function_name=self.current_function,
            question=question
        )
        response = self.llm.invoke(messages)
        return response.content.strip() == "A"

    def choose_function(self, question):
        response = chat_llm_with_ragg(
            task="function_calling",
            params={
                "question": question,
                "tool_description": self.tool_description
            }
        ).strip()

        if response not in self.tools.keys():
            raise ValueError(f"Không tìm thấy function: {response}")

        print(f"Assistant: Đã chọn function: {response}")
        return response

    def call(self, question):
        if not self.current_function:
            self.current_function = self.choose_function(question)
        else:
            if not self.check_same_function(question):
                print("Assistant: Chủ đề mới -> Đang chọn lại function...")
                self.current_function = self.choose_function(question)

        return self.tools[self.current_function].invoke(question=question)

# Test
if __name__ == "__main__":
    selector = ToolSelector(llm=llm, tools=tools)

    while True:
        user_input = input("\nUser: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Assistant: Tạm biệt!")
            break
        if user_input.lower() in ["reset", "đổi chủ đề"]:
            selector.current_function = None
            print("Assistant: Đã đặt lại chủ đề.")
            continue

        try:
            answer = selector.call(user_input)
            print("Trợ lý:", answer)
        except Exception as e:
            print("Lỗi:", str(e))