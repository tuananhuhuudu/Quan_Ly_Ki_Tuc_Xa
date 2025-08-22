from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai.orchestrator.tool_selector import ToolSelector
from ai.tool import QuyDinh
from ai.config.config import llm

class QuestionRequest(BaseModel):
    question: str

tools = {
    "QuyDinh": QuyDinh.QuyDinh_RAGG,
}
selector = ToolSelector(llm=llm, tools=tools)

def ask_question_helper(question: str) -> str:
    """Gọi ToolSelector để lấy câu trả lời"""
    return selector.call(question=question)

def reset_topic_helper() -> None:
    """Đặt lại chủ đề hiện tại"""
    selector.current_function = None
    return selector.current_function

router = APIRouter(prefix="/chatbot", tags=["ChatBot"])

@router.post("/ask")
def ask_question(req: QuestionRequest):
    try:
        answer = ask_question_helper(req.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset")
def reset_topic():
    reset_topic_helper()
    return {"message": "Đã đặt lại chủ đề."}
