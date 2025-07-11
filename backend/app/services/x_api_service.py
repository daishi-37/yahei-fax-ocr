import requests
from typing import Dict, Any
from app.core import settings


class XApiService:
    """X-API連携サービス（モック実装）"""
    
    async def upload_pdf(self, pdf_file_path: str) -> Dict[str, Any]:
        """PDFファイルをX-APIにアップロード（モック）"""
        try:
            # モック実装 - 実際のAPI呼び出しはコメントアウト
            """
            with open(pdf_file_path, 'rb') as f:
                files = {'file': f}
                headers = {'Authorization': f'Bearer {settings.X_API_KEY}'}
                response = requests.post(settings.X_API_URL, files=files, headers=headers)
                return response.json()
            """
            
            # モックレスポンス
            return {
                "status": "success",
                "file_id": f"mock_file_id_{pdf_file_path.split('/')[-1]}",
                "upload_url": f"{settings.X_API_URL}/files/mock_file_id",
                "message": "PDF uploaded successfully (mock)"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Upload failed: {str(e)}"
            }
