import os
from typing import Optional
import fitz  # PyMuPDF
from app.core.config import settings


class PDFService:
    """PDF 처리 서비스"""

    def __init__(self):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """PDF에서 텍스트 추출"""
        try:
            doc = fitz.open(pdf_path)
            text_parts = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                text_parts.append(text)

            doc.close()

            full_text = "\n\n".join(text_parts)
            return full_text

        except Exception as e:
            print(f"PDF 텍스트 추출 오류: {e}")
            return None

    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """업로드된 파일 저장"""
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        return file_path

    def delete_file(self, file_path: str):
        """파일 삭제"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"파일 삭제 오류: {e}")

    def extract_metadata(self, pdf_path: str) -> dict:
        """PDF 메타데이터 추출"""
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata

            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "page_count": len(doc),
            }

        except Exception as e:
            print(f"PDF 메타데이터 추출 오류: {e}")
            return {}


# 싱글톤 인스턴스
pdf_service = PDFService()
