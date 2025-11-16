import os
import pickle
from typing import List, Tuple, Optional
import faiss
import numpy as np
from app.core.config import settings
from .embeddings import embedding_service


class VectorStoreService:
    """FAISS 벡터 저장소 서비스"""

    def __init__(self):
        self.index = None
        self.documents = []  # 문서 메타데이터 저장
        self.dimension = embedding_service.get_dimension()
        self.index_path = os.path.join(settings.VECTOR_DB_PATH, "faiss_index")
        self.metadata_path = os.path.join(settings.VECTOR_DB_PATH, "metadata.pkl")

        # 디렉토리 생성
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)

        # 기존 인덱스 로드 또는 새로 생성
        self.load_or_create_index()

    def load_or_create_index(self):
        """기존 인덱스 로드 또는 새로 생성"""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.load_index()
        else:
            self.create_new_index()

    def create_new_index(self):
        """새 FAISS 인덱스 생성"""
        # L2 거리 기반 인덱스 생성
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []

    def add_documents(
        self, texts: List[str], metadata: List[dict]
    ) -> List[int]:
        """문서를 벡터 스토어에 추가"""
        if not texts:
            return []

        # 텍스트 임베딩
        embeddings = embedding_service.embed_texts(texts)
        embeddings_array = np.array(embeddings).astype("float32")

        # FAISS 인덱스에 추가
        start_id = len(self.documents)
        self.index.add(embeddings_array)

        # 메타데이터 저장
        for i, meta in enumerate(metadata):
            self.documents.append(
                {
                    "id": start_id + i,
                    "text": texts[i],
                    **meta,
                }
            )

        # 자동 저장
        self.save_index()

        return list(range(start_id, start_id + len(texts)))

    def search(
        self, query: str, k: int = 5
    ) -> List[Tuple[dict, float]]:
        """유사도 검색"""
        if self.index.ntotal == 0:
            return []

        # 쿼리 임베딩
        query_embedding = embedding_service.embed_text(query)
        query_array = np.array([query_embedding]).astype("float32")

        # 검색
        distances, indices = self.index.search(query_array, k)

        # 결과 반환
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(distances[0][i])))

        return results

    def delete_by_paper_id(self, paper_id: int):
        """특정 논문의 모든 청크 삭제"""
        # FAISS는 직접 삭제를 지원하지 않으므로, 재구축
        remaining_docs = [
            doc for doc in self.documents if doc.get("paper_id") != paper_id
        ]

        if len(remaining_docs) == len(self.documents):
            return  # 삭제할 문서 없음

        # 새 인덱스 생성
        self.create_new_index()

        # 남은 문서 다시 추가
        if remaining_docs:
            texts = [doc["text"] for doc in remaining_docs]
            metadata = [
                {k: v for k, v in doc.items() if k not in ["id", "text"]}
                for doc in remaining_docs
            ]
            self.add_documents(texts, metadata)

    def save_index(self):
        """인덱스와 메타데이터 저장"""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.documents, f)

    def load_index(self):
        """저장된 인덱스 로드"""
        self.index = faiss.read_index(self.index_path)
        with open(self.metadata_path, "rb") as f:
            self.documents = pickle.load(f)

    def clear(self):
        """모든 인덱스 및 문서 삭제"""
        self.create_new_index()
        self.save_index()


# 싱글톤 인스턴스
vectorstore_service = VectorStoreService()
