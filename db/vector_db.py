import pickle
import numpy as np
import openai
from core.config import settings
import os
from typing import List, Dict, Any

# 持久化文件路径保持不变
DB_DIR = "./vector_db_data"
VECTORS_FILE = os.path.join(DB_DIR, "vectors.npy")
METADATA_FILE = os.path.join(DB_DIR, "metadata.pkl")

class SimpleVectorDB:
    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        
        # ---- 核心改动：初始化API客户端，而不是本地模型 ----
        self.embedding_client = openai.OpenAI(
            base_url=settings.embedding.base_url,
            api_key=settings.embedding.api_key
        )
        self.embedding_model_name = settings.embedding.model_name
        # ----------------------------------------------------

        self.vectors = np.array([])
        self.metadata = []
        self._load()

    def _embed(self, texts: List[str]) -> np.ndarray:
        """
        ---- 核心改动：使用API进行向量化 ----
        将文本列表通过API调用转换为向量矩阵，并进行归一化。
        """
        try:
            # 调用OpenAI API
            response = self.embedding_client.embeddings.create(
                model=self.embedding_model_name,
                input=texts
            )
            # 从响应中提取嵌入向量
            embeddings = [item.embedding for item in response.data]
            embeddings_np = np.array(embeddings, dtype=np.float32)

            # 归一化向量以用于余弦相似度计算
            norms = np.linalg.norm(embeddings_np, axis=1, keepdims=True)
            return embeddings_np / norms

        except Exception as e:
            print(f"Error calling embedding API: {e}")
            # 返回一个空数组或根据需要处理错误
            return np.array([])
        # ------------------------------------------------

    def _load(self):
        """从磁盘加载向量和元数据 (此函数无需改动)"""
        if os.path.exists(VECTORS_FILE) and os.path.exists(METADATA_FILE):
            print("Loading existing vector database from disk...")
            self.vectors = np.load(VECTORS_FILE)
            with open(METADATA_FILE, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"Loaded {len(self.metadata)} documents.")
        else:
            print("No existing database found. Starting fresh.")
            self.vectors = np.array([])
            self.metadata = []

    def _save(self):
        """将当前的向量和元数据保存到磁盘 (此函数无需改动)"""
        if not self.metadata:
            return
        np.save(VECTORS_FILE, self.vectors)
        with open(METADATA_FILE, "wb") as f:
            pickle.dump(self.metadata, f)

    def add_document(self, document: str, metadata: Dict[str, Any]):
        """添加一个新文档到数据库 (此函数逻辑无需改动)"""
        new_vector = self._embed([document])
        
        # 如果API调用失败，_embed会返回空数组
        if new_vector.size == 0:
            print(f"Failed to embed document, skipping add.")
            return

        if self.vectors.size == 0:
            self.vectors = new_vector
        else:
            self.vectors = np.vstack([self.vectors, new_vector])
        
        metadata['document'] = document
        self.metadata.append(metadata)
        
        self._save()
        print(f"Added new document. Total documents: {len(self.metadata)}")

    def query(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """查询最相似的k个文档 (此函数逻辑无需改动)"""
        if len(self.metadata) == 0:
            return []

        query_vector = self._embed([query_text])
        
        if query_vector.size == 0:
            print(f"Failed to embed query, returning empty results.")
            return []

        similarities = np.dot(self.vectors, query_vector.T).flatten()
        top_k_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in top_k_indices:
            results.append({
                "similarity": float(similarities[idx]),
                "metadata": self.metadata[idx]
            })
        return results

# 创建全局客户端实例
vector_db_client = SimpleVectorDB()