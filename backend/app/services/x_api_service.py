import requests
from typing import Dict, Any, Optional
from pathlib import Path
import os
from app.core import settings


class XApiService:
    """X-API連携サービス"""
    
    def __init__(self):
        self.base_url = settings.X_API_URL
        self.api_key = settings.X_API_KEY
        
    async def upload_file(self, file_path: str, expire_hours: int = 24) -> Dict[str, Any]:
        """
        ファイルをX-APIにアップロード
        
        Args:
            file_path (str): アップロードするファイルのパス
            expire_hours (int): ファイルの有効期限（時間）、デフォルト24時間
            
        Returns:
            Dict[str, Any]: アップロード結果
        """
        try:
            # ファイルの存在確認
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "message": f"ファイルが見つかりません: {file_path}"
                }
            
            # ヘッダー設定
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # ファイルとデータの準備
            with open(file_path, 'rb') as file:
                files = {
                    'file': (os.path.basename(file_path), file, 'application/octet-stream')
                }
                data = {
                    'expire_hours': expire_hours
                }
                
                # API呼び出し
                response = requests.post(
                    self.base_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=30
                )
                
                # レスポンス処理
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "success",
                        "data": result,
                        "message": "ファイルのアップロードが成功しました"
                    }
                else:
                    return {
                        "status": "error",
                        "status_code": response.status_code,
                        "message": f"アップロードに失敗しました: {response.text}",
                        "response": response.text
                    }
                    
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "リクエストがタイムアウトしました"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "API接続エラーが発生しました"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"予期しないエラーが発生しました: {str(e)}"
            }
    
    async def upload_pdf(self, pdf_file_path: str, expire_hours: int = 24) -> Dict[str, Any]:
        """
        PDFファイルをX-APIにアップロード（既存メソッドとの互換性維持）
        
        Args:
            pdf_file_path (str): PDFファイルのパス
            expire_hours (int): ファイルの有効期限（時間）
            
        Returns:
            Dict[str, Any]: アップロード結果
        """
        return await self.upload_file(pdf_file_path, expire_hours)
    
    def get_file_info(self, response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        アップロードレスポンスからファイル情報を抽出
        
        Args:
            response_data (Dict[str, Any]): APIレスポンスデータ
            
        Returns:
            Optional[Dict[str, Any]]: ファイル情報
        """
        if response_data.get("status") == "success" and "data" in response_data:
            data = response_data["data"]
            return {
                "file_id": data.get("data"),
                "title": data.get("title"),
                "url": data.get("url"),
                "start_datetime": data.get("start_datetime"),
                "end_datetime": data.get("end_datetime")
            }
        return None
