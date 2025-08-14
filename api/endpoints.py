# local_memory_service/api/endpoints.py

from fastapi import APIRouter, status
from pydantic import BaseModel, Field
import threading
from typing import List, Optional, Dict, Any

from services.state_manager import state_manager
from services.rag_service import rag_task, summary_task
from db.vector_db import vector_db_client  # 导入新的DB客户端

router = APIRouter()

# --- Pydantic 模型定义 ---
class EnableRequest(BaseModel):
    enabled: bool

class ProcessTaskRequest(BaseModel):
    task_description: str
    history: List[str] = []

class ProcessTaskResponse(BaseModel):
    rag_context: Optional[str]
    summary: Optional[str]

# 新增：用于添加文档的请求模型
class AddDocumentRequest(BaseModel):
    document: str
    source: str = "user_provided"

# --- API 端点 ---
@router.post("/enable", status_code=status.HTTP_200_OK)
def toggle_service(request: EnableRequest):
    state_manager.set_enabled(request.enabled)
    return {"status": "success", "enabled": state_manager.is_enabled()}

# 新增：添加文档的端点
@router.post("/add_document", status_code=status.HTTP_201_CREATED)
def add_document(request: AddDocumentRequest):
    """接收并处理要添加到向量数据库的文档"""
    metadata = {"source": request.source}
    vector_db_client.add_document(request.document, metadata)
    return {"status": "success", "message": "Document added."}

@router.post("/process_task", response_model=ProcessTaskResponse)
def process_task(request: ProcessTaskRequest):
    results: Dict[str, Any] = {'rag_context': None, 'summary': None}
    
    rag_thread = threading.Thread(target=rag_task, args=(request.task_description, results))
    summary_thread = threading.Thread(target=summary_task, args=(request.history, results))

    rag_thread.start()
    summary_thread.start()

    rag_thread.join()
    summary_thread.join()

    return ProcessTaskResponse(**results)