"""
PubMed Search Service
"""
from typing import List, Optional
from datetime import datetime
from Bio import Entrez
from app.core.config import settings
from app.core.logging import app_logger as logger
from app.shared.infrastructure.cache.service import cache


class PubMedService:
    """PubMed API 서비스"""

    def __init__(self):
        Entrez.email = settings.PUBMED_EMAIL
        if hasattr(settings, 'PUBMED_API_KEY') and settings.PUBMED_API_KEY:
            Entrez.api_key = settings.PUBMED_API_KEY

    async def search_papers(
        self, query: str, max_results: int = 20, sort: str = "relevance"
    ) -> List[dict]:
        """논문 검색 (캐싱 지원)"""
        # 캐시 확인
        cache_key = cache._generate_key("pubmed", query=query, max=max_results, sort=sort)
        cached = await cache.get(cache_key)
        if cached:
            logger.info(f"PubMed 검색 캐시 HIT: {query}")
            return cached

        try:
            # 검색 실행
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort=sort,
            )
            record = Entrez.read(handle)
            handle.close()

            id_list = record["IdList"]

            if not id_list:
                return []

            # 논문 상세 정보 가져오기
            results = self.fetch_papers_by_ids(id_list)

            # 캐시에 저장 (1시간)
            await cache.set(cache_key, results, expire=3600)

            logger.info(f"PubMed 검색 완료: {query} ({len(results)}개)")
            return results

        except Exception as e:
            logger.error(f"PubMed 검색 오류: {e}")
            return []

    def fetch_papers_by_ids(self, pubmed_ids: List[str]) -> List[dict]:
        """PubMed ID로 논문 정보 가져오기"""
        try:
            # 상세 정보 가져오기
            handle = Entrez.efetch(
                db="pubmed", id=",".join(pubmed_ids), retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()

            papers = []
            for article in records["PubmedArticle"]:
                paper = self._parse_article(article)
                if paper:
                    papers.append(paper)

            return papers

        except Exception as e:
            logger.error(f"PubMed 정보 가져오기 오류: {e}")
            return []

    def _parse_article(self, article: dict) -> Optional[dict]:
        """PubMed 논문 파싱"""
        try:
            medline = article.get("MedlineCitation", {})
            pubmed_data = article.get("PubmedData", {})

            # 기본 정보
            pmid = str(medline.get("PMID", ""))
            article_data = medline.get("Article", {})

            # 제목
            title = article_data.get("ArticleTitle", "")

            # 저자
            author_list = article_data.get("AuthorList", [])
            authors = []
            for author in author_list:
                if "LastName" in author:
                    name = f"{author.get('LastName', '')} {author.get('ForeName', '')}"
                    authors.append(name.strip())

            # 초록
            abstract_list = article_data.get("Abstract", {}).get("AbstractText", [])
            abstract = " ".join([str(ab) for ab in abstract_list])

            # 저널
            journal = article_data.get("Journal", {})
            journal_title = journal.get("Title", "")

            # 발행일
            pub_date = article_data.get("ArticleDate", [{}])[0] if article_data.get("ArticleDate") else {}
            publication_date = None
            if pub_date:
                year = pub_date.get("Year")
                month = pub_date.get("Month", "01")
                day = pub_date.get("Day", "01")
                if year:
                    try:
                        publication_date = datetime(int(year), int(month), int(day)).isoformat()
                    except:
                        pass

            # DOI
            doi = None
            article_id_list = pubmed_data.get("ArticleIdList", [])
            for article_id in article_id_list:
                if hasattr(article_id, 'attributes') and article_id.attributes.get("IdType") == "doi":
                    doi = str(article_id)
                    break

            # 키워드
            keywords = []
            keyword_list = medline.get("KeywordList", [[]])
            if keyword_list:
                keywords = [str(kw) for kw in keyword_list[0]]

            return {
                "pubmed_id": pmid,
                "title": title,
                "authors": ", ".join(authors),
                "abstract": abstract,
                "journal": journal_title,
                "publication_date": publication_date,
                "doi": doi,
                "keywords": keywords,
                "source": "pubmed",
            }

        except Exception as e:
            logger.error(f"논문 파싱 오류: {e}")
            return None


# 싱글톤 인스턴스
pubmed_service = PubMedService()
