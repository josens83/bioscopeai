from typing import List, Optional
from datetime import datetime
from Bio import Entrez
import requests
from app.core.config import settings


class PubMedService:
    """PubMed API 서비스"""

    def __init__(self):
        Entrez.email = settings.PUBMED_EMAIL
        if settings.PUBMED_API_KEY:
            Entrez.api_key = settings.PUBMED_API_KEY

    def search_papers(
        self, query: str, max_results: int = 20, sort: str = "relevance"
    ) -> List[dict]:
        """논문 검색"""
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
            return self.fetch_papers_by_ids(id_list)

        except Exception as e:
            print(f"PubMed 검색 오류: {e}")
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
            print(f"PubMed 정보 가져오기 오류: {e}")
            return []

    def _parse_article(self, article: dict) -> Optional[dict]:
        """PubMed 응답에서 논문 정보 파싱"""
        try:
            medline = article["MedlineCitation"]
            pubmed_data = article.get("PubmedData", {})

            # 기본 정보
            pubmed_id = str(medline["PMID"])
            article_data = medline["Article"]

            # 제목
            title = article_data.get("ArticleTitle", "")

            # 초록
            abstract_text = ""
            if "Abstract" in article_data:
                abstract_parts = article_data["Abstract"].get("AbstractText", [])
                if abstract_parts:
                    abstract_text = " ".join(
                        [str(part) for part in abstract_parts]
                    )

            # 저자
            authors = []
            if "AuthorList" in article_data:
                for author in article_data["AuthorList"]:
                    if "LastName" in author and "ForeName" in author:
                        authors.append(
                            f"{author['LastName']} {author['ForeName']}"
                        )

            # 출판일
            publication_date = None
            if "ArticleDate" in article_data:
                date_info = article_data["ArticleDate"][0]
                try:
                    publication_date = datetime(
                        int(date_info.get("Year", 1900)),
                        int(date_info.get("Month", 1)),
                        int(date_info.get("Day", 1)),
                    )
                except:
                    pass

            # 저널
            journal = article_data.get("Journal", {}).get("Title", "")

            # DOI
            doi = None
            if "ELocationID" in article_data:
                for elocation in article_data["ELocationID"]:
                    if elocation.attributes.get("EIdType") == "doi":
                        doi = str(elocation)
                        break

            # 키워드
            keywords = []
            if "KeywordList" in medline:
                for keyword_list in medline["KeywordList"]:
                    keywords.extend([str(k) for k in keyword_list])

            return {
                "pubmed_id": pubmed_id,
                "title": title,
                "abstract": abstract_text,
                "authors": ", ".join(authors),
                "publication_date": publication_date,
                "journal": journal,
                "doi": doi,
                "keywords": keywords,
                "source": "pubmed",
            }

        except Exception as e:
            print(f"논문 파싱 오류: {e}")
            return None

    def get_paper_by_pubmed_id(self, pubmed_id: str) -> Optional[dict]:
        """단일 PubMed ID로 논문 가져오기"""
        papers = self.fetch_papers_by_ids([pubmed_id])
        return papers[0] if papers else None


# 싱글톤 인스턴스
pubmed_service = PubMedService()
