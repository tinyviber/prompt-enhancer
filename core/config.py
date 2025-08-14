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
        """
        Load configuration with the following precedence (highest -> lowest):
        1. Environment variables (useful for CI and secrets)
        2. config/llm_config.json file

        Environment variable names supported:
        - CHAT_API_TYPE, CHAT_BASE_URL, CHAT_API_KEY, CHAT_MODEL_NAME
        - EMBEDDING_PROVIDER, EMBEDDING_BASE_URL, EMBEDDING_API_KEY, EMBEDDING_MODEL_NAME
        """
        config_path = Path(__file__).parent.parent / "config" / "llm_config.json"

        config_data = {}
        if config_path.exists():
            with open(config_path, 'r') as f:
                try:
                    config_data = json.load(f)
                except json.JSONDecodeError:
                    raise ValueError(f"Configuration file is not valid JSON: {config_path}")

        # Helper to read env with fallback into config_data
        def env_or_config(env_name: str, *path, default=None):
            val = os.environ.get(env_name)
            if val is not None:
                return val
            # navigate nested dict if provided
            if path:
                node = config_data
                for p in path:
                    if not isinstance(node, dict) or p not in node:
                        return default
                    node = node[p]
                return node
            return default

        # Chat LLM
        chat = {
            'api_type': env_or_config('CHAT_API_TYPE', 'chat_llm', 'api_type', default='openai_compatible'),
            'base_url': env_or_config('CHAT_BASE_URL', 'chat_llm', 'base_url', default=''),
            'api_key': env_or_config('CHAT_API_KEY', 'chat_llm', 'api_key', default=''),
            'model_name': env_or_config('CHAT_MODEL_NAME', 'chat_llm', 'model_name', default=''),
        }

        # Embedding
        embedding = {
            'provider': env_or_config('EMBEDDING_PROVIDER', 'embedding', 'provider', default='openai'),
            'base_url': env_or_config('EMBEDDING_BASE_URL', 'embedding', 'base_url', default=''),
            'api_key': env_or_config('EMBEDDING_API_KEY', 'embedding', 'api_key', default=''),
            'model_name': env_or_config('EMBEDDING_MODEL_NAME', 'embedding', 'model_name', default=''),
        }

        # Validate minimal required fields
        if not chat['base_url'] or not chat['api_key'] or not chat['model_name']:
            raise ValueError('Chat LLM configuration incomplete. Provide CHAT_* env vars or config/llm_config.json')

        self.chat_llm = ChatLLMConfig(**chat)
        self.embedding = EmbeddingConfig(**embedding)

import os

# 创建全局单例
settings = Settings()
