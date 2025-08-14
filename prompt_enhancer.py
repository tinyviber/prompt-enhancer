import requests
import json
import openai
import pathlib
import sys
from typing import Dict, Any

from core.config import settings

# 使用全局 settings（支持环境变量覆盖）
ORCHESTRATOR_LLM_CONFIG = {
    'base_url': settings.chat_llm.base_url,
    'api_key': settings.chat_llm.api_key,
    'model_name': settings.chat_llm.model_name,
}

# 配置微服务地址
MICROSERVICE_URL = "http://127.0.0.1:8000"

# 初始化客户端
orchestrator_llm_client = openai.OpenAI(
    base_url=ORCHESTRATOR_LLM_CONFIG['base_url'],
    api_key=ORCHESTRATOR_LLM_CONFIG['api_key'],
)


def get_rag_context(raw_prompt: str) -> str | None:
    """第一阶段：调用微服务进行RAG检索。"""
    endpoint = f"{MICROSERVICE_URL}/process_task"
    payload = {"task_description": raw_prompt, "history": []}
    
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("rag_context")
    except requests.exceptions.RequestException as e:
        # 在库函数中，我们向上抛出异常，让调用者（UI或CLI）来决定如何处理
        raise ConnectionError(f"Error calling the local memory service: {e}")


def refine_prompt_with_llm(raw_prompt: str, rag_context: str) -> str:
    """第二阶段：使用Orchestrator LLM提炼上下文。"""
    system_prompt = (
        "You are an expert prompt engineering assistant. Your task is to analyze an original user prompt and a set of retrieved documents (context), "
        "and then create a new, enhanced prompt. \n\n"
        "Follow these instructions carefully:\n"
        "1.  Read the 'Original User Prompt' to understand the user's core question or goal.\n"
        "2.  Analyze the 'Retrieved Context'. Identify ONLY the pieces of information that are directly relevant and useful for answering the original prompt.\n"
        "3.  IGNORE any context that is irrelevant, redundant, or confusing.\n"
        "4.  Synthesize the useful information from the context with the original prompt.\n"
        "5.  Your final output MUST be ONLY the new, enhanced prompt, ready to be sent to another powerful AI for the final answer. Do not answer the prompt yourself. Do not add any conversational fluff or explanations like 'Here is the enhanced prompt:'. Just output the prompt itself."
    )

    user_content = (
        f"**Original User Prompt:**\n{raw_prompt}\n\n"
        f"**Retrieved Context:**\n---\n{rag_context}\n---"
    )

    try:
        response = orchestrator_llm_client.chat.completions.create(
            model=ORCHESTRATOR_LLM_CONFIG['model_name'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # 同样，向上抛出异常
        raise RuntimeError(f"An unexpected error occurred during prompt refinement: {e}")
