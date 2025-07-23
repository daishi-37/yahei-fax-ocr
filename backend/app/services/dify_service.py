import requests
import aiohttp
import asyncio
from typing import Dict, Any, BinaryIO
from app.core import settings
import os


class DifyService:
    """Dify OCRサービス"""
    
    def __init__(self):
        self.base_url = settings.DIFY_BASE_URL
        self.api_token = settings.DIFY_API_TOKEN
        self.api_token_search = settings.DIFY_API_TOKEN_SEARCH
        
    async def upload_file(self, file_path: str) -> str:
        """ファイルをDifyにアップロード"""
        try:
            url = f"{self.base_url}/v1/files/upload"
            
            # ファイルを読み込み
            with open(file_path, 'rb') as file:
                # FormDataを作成
                data = aiohttp.FormData()
                data.add_field('file', file, filename=os.path.basename(file_path))
                data.add_field('user', 'fax-ocr-user')
                
                headers = {
                    'Authorization': f'Bearer {self.api_token}'
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=data, headers=headers) as response:
                        if response.status not in [200, 201]:
                            error_text = await response.text()
                            raise Exception(f"ファイルアップロードエラー: {response.status} {response.reason} - {error_text}")
                        
                        response_data = await response.json()
                        print(' === Dify file upload response === ')
                        print('Uploaded file data:', response_data)
                        
                        return response_data.get('id')
                        
        except Exception as e:
            print(f"ファイルアップロードでエラーが発生しました: {e}")
            raise e
    
    async def process_ocr(self, file_id: str, file_type: str = "document") -> Dict[str, Any]:
        """アップロードされたファイルのOCR処理をDifyで実行"""
        try:
            url = f"{self.base_url}/v1/workflows/run"
            
            request_body = {
                "inputs": {
                    "img": {
                        "type": file_type,
                        "transfer_method": "local_file",
                        "upload_file_id": file_id
                    }
                },
                "response_mode": "blocking",
                "user": "fax-ocr-user"
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_body, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"ワークフロー実行エラー: {response.status} {response.reason} - {error_text}")
                    
                    response_data = await response.json()
                    print(' === Dify OCR processing response === ')
                    print(response_data)
                    
                    # outputsを取得
                    outputs = response_data.get('data', {}).get('outputs') or response_data.get('outputs', {})
                    
                    return outputs
                    
        except Exception as e:
            print(f"OCR処理でエラーが発生しました: {e}")
            return {
                "status": "error",
                "message": f"OCR processing failed: {str(e)}"
            }
    
    async def search_client_fuzzy(self, ocr_client_info: str, notion_clients: list) -> Dict[str, Any]:
        """OCR結果のクライアント情報とNotionクライアントDBの情報を使用してDifyで曖昧検索を実行"""
        try:
            url = f"{self.base_url}/v1/workflows/run"
            
            # Difyワークフローに送信するデータ
            # notion_clientsをJSON文字列に変換
            import json
            notion_clients_str = json.dumps(notion_clients, ensure_ascii=False)
            
            request_body = {
                "inputs": {
                    "ocr_client_name": ocr_client_info,
                    "clients": notion_clients_str,
                },
                "response_mode": "blocking",
                "user": "fax-ocr-fuzzy-search"
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_token_search}',
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_body, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"曖昧検索エラー: {response.status} {response.reason} - {error_text}")
                    
                    response_data = await response.json()
                    print(' === Dify fuzzy search response === ')
                    print(response_data)
                    
                    # outputsを取得
                    outputs = response_data.get('data', {}).get('outputs') or response_data.get('outputs', {})
                    
                    return outputs
                    
        except Exception as e:
            print(f"曖昧検索でエラーが発生しました: {e}")
            return {
                "status": "error",
                "message": f"Fuzzy search failed: {str(e)}"
            }
