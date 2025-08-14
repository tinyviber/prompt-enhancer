import openai
from core.config import settings

# 使用新的 chat_llm 配置来初始化客户端
client = openai.OpenAI(
    base_url=settings.chat_llm.base_url,
    api_key=settings.chat_llm.api_key,
)

def is_task_relevant(task: str) -> bool:
    prompt = f"Is the following task related to programming, software development, or technology? Answer with only 'yes' or 'no'.\n\nTask: '{task}'"
    try:
        response = client.chat.completions.create(
            # 使用 chat_llm 的模型名称
            model=settings.chat_llm.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0.0
        )
        answer = response.choices[0].message.content.strip().lower()
        print(f"LLM relevance check for '{task}': {answer}")
        return "yes" in answer
    except Exception as e:
        print(f"Error checking relevance: {e}")
        return False

def summarize_history(history: list[str]) -> str:
    history_text = "\n".join(history)
    prompt = f"Please provide a concise summary of the following conversation:\n\n{history_text}"
    try:
        response = client.chat.completions.create(
            # 使用 chat_llm 的模型名称
            model=settings.chat_llm.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.2
        )
        summary = response.choices[0].message.content.strip()
        print(f"LLM generated summary.")
        return summary
    except Exception as e:
        print(f"Error summarizing history: {e}")
        return "Summary generation failed."