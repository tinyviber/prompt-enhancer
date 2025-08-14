import json
from pathlib import Path
from pydantic import BaseModel, Field

class ChatLLMConfig(BaseModel):
    api_type: str
    base_url: str
    api_key: str
    model_name: str

class EmbeddingConfig(BaseModel):
    provider: str
    base_url: str
    api_key: str
    model_name: str

class Settings:
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config" / "llm_config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # 分别加载聊天和嵌入的配置
        self.chat_llm = ChatLLMConfig(**config_data['chat_llm'])
        self.embedding = EmbeddingConfig(**config_data['embedding'])

# 创建全局单例
settings = Settings()