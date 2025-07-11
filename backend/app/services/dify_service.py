import requests
from typing import Dict, Any
from app.core import settings


class DifyService:
    """Dify OCRサービス（モック実装）"""
    
    async def process_ocr(self, pdf_file_path: str) -> Dict[str, Any]:
        """PDFファイルのOCR処理をDifyで実行（モック）"""
        try:
            # モック実装 - 実際のAPI呼び出しはコメントアウト
            """
            with open(pdf_file_path, 'rb') as f:
                files = {'file': f}
                headers = {'Authorization': f'Bearer {settings.DIFY_API_KEY}'}
                response = requests.post(settings.DIFY_API_URL, files=files, headers=headers)
                return response.json()
            """
            
            # モックレスポンス
            filename = pdf_file_path.split('/')[-1]
            return {
                "status": "success",
                "ocr_id": f"mock_ocr_id_{filename}",
                "extracted_text": f"Mock extracted text from {filename}",
                "confidence": 0.95,
                "pages": 1,
                "processing_time": "2.5s",
                "message": "OCR processing completed successfully (mock)"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"OCR processing failed: {str(e)}"
            }
