from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings
from .vectorstore import vectorstore_service


class RAGPipeline:
    """RAG 파이프라인 - 검색 증강 생성"""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4",
            temperature=0.3,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split_text(self, text: str) -> List[str]:
        """텍스트를 청크로 분할"""
        return self.text_splitter.split_text(text)

    async def answer_question(
        self, question: str, paper_id: Optional[int] = None, k: int = 5
    ) -> dict:
        """질문에 답변 생성"""
        # 유사 문서 검색
        search_results = vectorstore_service.search(question, k=k)

        if not search_results:
            return {
                "answer": "관련 문서를 찾을 수 없습니다.",
                "sources": [],
                "confidence": 0.0,
            }

        # paper_id가 지정된 경우 해당 논문에서만 검색
        if paper_id:
            search_results = [
                (doc, score)
                for doc, score in search_results
                if doc.get("paper_id") == paper_id
            ]

        if not search_results:
            return {
                "answer": "해당 논문에서 관련 정보를 찾을 수 없습니다.",
                "sources": [],
                "confidence": 0.0,
            }

        # 컨텍스트 구성
        context = "\n\n".join([doc["text"] for doc, _ in search_results[:3]])

        # 프롬프트 구성
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 생물의학 논문 전문가입니다. 주어진 논문 내용을 바탕으로 정확하고 상세하게 답변해주세요.",
                ),
                (
                    "user",
                    """다음 논문 내용을 참고하여 질문에 답변해주세요:

<논문 내용>
{context}
</논문 내용>

질문: {question}

답변 시 다음을 포함해주세요:
1. 명확하고 구체적인 답변
2. 논문의 어느 부분을 참고했는지
3. 필요시 추가 설명이나 맥락""",
                ),
            ]
        )

        # LLM 호출
        chain = prompt | self.llm
        response = await chain.ainvoke({"context": context, "question": question})

        # 소스 정보 구성
        sources = [
            {
                "paper_id": doc.get("paper_id"),
                "chunk_id": doc.get("id"),
                "text": doc["text"][:200] + "...",
                "score": float(score),
            }
            for doc, score in search_results[:3]
        ]

        return {
            "answer": response.content,
            "sources": sources,
            "confidence": 1.0 - min(search_results[0][1] / 10, 1.0),
        }

    async def summarize_paper(self, paper_text: str, paper_title: str) -> dict:
        """논문 요약 생성"""
        # 논문을 청크로 분할
        chunks = self.split_text(paper_text)

        if not chunks:
            return {"summary": "요약할 내용이 없습니다."}

        # 초록만 사용하거나 전체 요약
        text_to_summarize = "\n".join(chunks[:5])  # 처음 5개 청크만 사용

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 생물의학 논문 요약 전문가입니다. 논문의 핵심 내용을 명확하게 요약해주세요.",
                ),
                (
                    "user",
                    """다음 논문을 요약해주세요:

제목: {title}

내용:
{text}

다음 항목을 포함하여 요약해주세요:
1. 연구 목적 및 배경
2. 연구 방법론
3. 주요 결과
4. 결론 및 시사점
5. 한계점

한국어로 작성하되, 전문 용어는 영어 원문을 병기해주세요.""",
                ),
            ]
        )

        chain = prompt | self.llm
        response = await chain.ainvoke({"title": paper_title, "text": text_to_summarize})

        return {"summary": response.content}

    async def compare_papers(
        self, paper_data: List[dict]
    ) -> dict:
        """여러 논문 비교 분석"""
        if len(paper_data) < 2:
            return {"comparison": "비교할 논문이 부족합니다. 최소 2개 이상 필요합니다."}

        if len(paper_data) > 10:
            return {"comparison": "최대 10개까지만 비교 가능합니다."}

        # 논문 정보 구성
        papers_info = "\n\n".join(
            [
                f"[논문 {i+1}]\n제목: {p['title']}\n초록: {p['abstract'][:500]}..."
                for i, p in enumerate(paper_data)
            ]
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 생물의학 논문 비교 분석 전문가입니다. 여러 논문을 체계적으로 비교 분석해주세요.",
                ),
                (
                    "user",
                    """다음 논문들을 비교 분석해주세요:

{papers_info}

다음 항목별로 비교표를 작성해주세요:
1. 연구 목적 및 배경
2. 연구 방법론
3. 주요 결과
4. 공통점과 차이점
5. 각 논문의 강점과 한계점
6. 연구 트렌드 및 시사점

마크다운 테이블 형식으로 작성해주세요.""",
                ),
            ]
        )

        chain = prompt | self.llm
        response = await chain.ainvoke({"papers_info": papers_info})

        return {"comparison": response.content}


# 싱글톤 인스턴스
rag_pipeline = RAGPipeline()
