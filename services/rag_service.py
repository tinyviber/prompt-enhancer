# local_memory_service/services/rag_service.py

from typing import Dict, Any, List

# 导入新的DB客户端和LLM服务
from db.vector_db import vector_db_client
from .llm_service import is_task_relevant, summarize_history


def rag_task(task_description: str, result_container: Dict[str, Any]):
    """
    RAG检索线程任务。
    """
    if is_task_relevant(task_description):
        # 使用我们自己的DB进行查询
        search_results = vector_db_client.query(task_description, k=2)
        
        if search_results:
            # 从结果中提取文档文本
            retrieved_docs = [res['metadata']['document'] for res in search_results]
            result_container['rag_context'] = "\n---\n".join(retrieved_docs)

def summary_task(history: List[str], result_container: Dict[str, Any]):
    """
    对话历史摘要线程任务。
    """
    if history:
        result_container['summary'] = summarize_history(history)