"""
向量存储 - Embedding 生成和存储
"""
import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from .logger import get_logger
from .config_loader import get_config

logger = get_logger(__name__)


class VectorStore:
    """向量存储，支持 FAISS/Chroma"""

    def __init__(self, store_type: Optional[str] = None, dimension: Optional[int] = None):
        self.config = get_config()
        self.store_type = store_type or self.config.get('vector_store.type', 'faiss')
        self.dimension = dimension or self.config.get('vector_store.dimension', 1536)
        self.index_path = self.config.get('vector_store.index_path', './data/vectors')

        # 确保目录存在
        Path(self.index_path).mkdir(parents=True, exist_ok=True)

        self.index = None
        self.id_to_metadata = {}
        self.next_id = 0

        self._init_store()

    def _init_store(self):
        """初始化向量存储"""
        if self.store_type == 'faiss':
            try:
                import faiss
                self.index = faiss.IndexFlatL2(self.dimension)
                logger.info(f"Initialized FAISS index with dimension {self.dimension}")
            except ImportError:
                logger.error("FAISS not installed. Run: pip install faiss-cpu")
                raise
        elif self.store_type == 'chroma':
            try:
                import chromadb
                self.client = chromadb.Client()
                self.collection = self.client.create_collection("embeddings")
                logger.info("Initialized Chroma vector store")
            except ImportError:
                logger.error("Chroma not installed. Run: pip install chromadb")
                raise
        else:
            raise ValueError(f"Unsupported vector store type: {self.store_type}")

    def add(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]) -> List[int]:
        """
        添加向量和元数据

        Args:
            embeddings: 向量列表
            metadata: 元数据列表

        Returns:
            添加的向量 ID 列表
        """
        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata must have the same length")

        ids = []

        if self.store_type == 'faiss':
            import faiss
            vectors = np.array(embeddings, dtype=np.float32)

            # 添加到索引
            start_id = self.next_id
            self.index.add(vectors)

            # 保存元数据
            for i, meta in enumerate(metadata):
                vec_id = start_id + i
                self.id_to_metadata[vec_id] = meta
                ids.append(vec_id)

            self.next_id += len(embeddings)

        elif self.store_type == 'chroma':
            # Chroma 使用字符串 ID
            ids = [str(self.next_id + i) for i in range(len(embeddings))]
            self.collection.add(
                embeddings=embeddings,
                metadatas=metadata,
                ids=ids
            )
            self.next_id += len(embeddings)

        logger.info(f"Added {len(embeddings)} vectors to store")
        return ids

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        搜索最相似的向量

        Args:
            query_embedding: 查询向量
            top_k: 返回前 k 个结果
            threshold: 相似度阈值（可选）

        Returns:
            [(id, distance, metadata), ...] 列表
        """
        if self.store_type == 'faiss':
            query_vector = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_vector, top_k)

            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # FAISS 返回 -1 表示没有更多结果
                    break

                # 转换距离为相似度（余弦相似度）
                similarity = 1 / (1 + dist)

                if threshold is None or similarity >= threshold:
                    metadata = self.id_to_metadata.get(int(idx), {})
                    results.append((int(idx), float(similarity), metadata))

            return results

        elif self.store_type == 'chroma':
            results_obj = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            results = []
            for i in range(len(results_obj['ids'][0])):
                vec_id = int(results_obj['ids'][0][i])
                distance = results_obj['distances'][0][i]
                similarity = 1 / (1 + distance)
                metadata = results_obj['metadatas'][0][i]

                if threshold is None or similarity >= threshold:
                    results.append((vec_id, similarity, metadata))

            return results

        return []

    def save(self, name: str = "default"):
        """保存索引到磁盘"""
        if self.store_type == 'faiss':
            import faiss
            index_file = os.path.join(self.index_path, f"{name}.index")
            metadata_file = os.path.join(self.index_path, f"{name}.metadata")

            faiss.write_index(self.index, index_file)

            with open(metadata_file, 'wb') as f:
                pickle.dump({
                    'id_to_metadata': self.id_to_metadata,
                    'next_id': self.next_id
                }, f)

            logger.info(f"Saved FAISS index to {index_file}")

        elif self.store_type == 'chroma':
            logger.info("Chroma persists automatically")

    def load(self, name: str = "default"):
        """从磁盘加载索引"""
        if self.store_type == 'faiss':
            import faiss
            index_file = os.path.join(self.index_path, f"{name}.index")
            metadata_file = os.path.join(self.index_path, f"{name}.metadata")

            if not os.path.exists(index_file):
                logger.warning(f"Index file not found: {index_file}")
                return

            self.index = faiss.read_index(index_file)

            with open(metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.id_to_metadata = data['id_to_metadata']
                self.next_id = data['next_id']

            logger.info(f"Loaded FAISS index from {index_file}")

        elif self.store_type == 'chroma':
            logger.info("Chroma loads automatically")

    def clear(self):
        """清空索引"""
        if self.store_type == 'faiss':
            self.index.reset()
            self.id_to_metadata = {}
            self.next_id = 0
            logger.info("Cleared FAISS index")

        elif self.store_type == 'chroma':
            self.client.delete_collection("embeddings")
            self.collection = self.client.create_collection("embeddings")
            self.next_id = 0
            logger.info("Cleared Chroma collection")
