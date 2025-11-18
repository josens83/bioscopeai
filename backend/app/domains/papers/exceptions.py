"""
Papers Domain Exceptions
"""
from fastapi import HTTPException, status


class PaperException(HTTPException):
    """논문 관련 기본 예외"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class PaperNotFoundException(HTTPException):
    """논문을 찾을 수 없음"""
    def __init__(self, paper_id: int = None):
        detail = f"논문을 찾을 수 없습니다 (ID: {paper_id})" if paper_id else "논문을 찾을 수 없습니다"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidPDFException(PaperException):
    """유효하지 않은 PDF 파일"""
    def __init__(self):
        super().__init__(detail="PDF 파일만 업로드 가능합니다")


class DuplicatePaperException(PaperException):
    """중복된 논문"""
    def __init__(self, doi: str = None):
        detail = f"이미 존재하는 논문입니다 (DOI: {doi})" if doi else "이미 존재하는 논문입니다"
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class PubMedSearchException(PaperException):
    """PubMed 검색 오류"""
    def __init__(self, message: str = "PubMed 검색 중 오류가 발생했습니다"):
        super().__init__(detail=message)


class PDFProcessingException(PaperException):
    """PDF 처리 오류"""
    def __init__(self, message: str = "PDF 처리 중 오류가 발생했습니다"):
        super().__init__(detail=message)
