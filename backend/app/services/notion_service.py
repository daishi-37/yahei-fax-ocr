from notion_client import Client
from typing import Dict, Any, Optional
from app.core import settings
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime


class NotionService:
    """Notion API連携サービス"""
    
    def __init__(self):
        if settings.NOTION_TOKEN:
            self.notion = Client(auth=settings.NOTION_TOKEN)
        else:
            self.notion = None
        
        # クライアントデータのキャッシュ
        self._clients_cache: Optional[list] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(minutes=5)  # キャッシュの有効期限（5分）
    
    async def get_all_clients(self, force_refresh: bool = False) -> list:
        """クライアントデータベースから全クライアント情報を取得
        
        Args:
            force_refresh: Trueの場合、キャッシュを無視して強制的に再取得
        
        Returns:
            クライアント情報のリスト
        """
        try:
            if not self.notion or not settings.NOTION_CLIENT_DATABASE_ID:
                return []
            
            # キャッシュが有効な場合はキャッシュから返す
            if not force_refresh and self._is_cache_valid():
                print("クライアントデータをキャッシュから取得")
                return self._clients_cache
            
            all_clients = []
            has_more = True
            start_cursor = None
            
            while has_more:
                # クライアントデータベースを取得
                params = {
                    "database_id": settings.NOTION_CLIENT_DATABASE_ID,
                    "page_size": 100
                }
                if start_cursor:
                    params["start_cursor"] = start_cursor
                
                response = self.notion.databases.query(**params)
                
                # 各クライアントの情報を抽出
                for page in response["results"]:
                    client_info = {
                        "id": page["id"],
                        "name": "",
                        "abbreviation": ""
                    }
                    
                    # クライアント名（タイトル）を取得
                    if "properties" in page:
                        for prop_name, prop_value in page["properties"].items():
                            if prop_value["type"] == "title" and prop_value["title"]:
                                client_info["name"] = prop_value["title"][0]["text"]["content"]
                                break
                        
                        # 略称を取得
                        if "略称" in page["properties"]:
                            abbrev_prop = page["properties"]["略称"]
                            if abbrev_prop["type"] == "rich_text" and abbrev_prop["rich_text"]:
                                client_info["abbreviation"] = abbrev_prop["rich_text"][0]["text"]["content"]
                    
                    if client_info["name"]:  # 名前がある場合のみ追加
                        all_clients.append(client_info)
                
                # 次のページがあるか確認
                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor", None)
            
            # キャッシュを更新
            self._clients_cache = all_clients
            self._cache_timestamp = datetime.now()
            print(f"クライアントデータをキャッシュに保存: {len(all_clients)}件")
            
            return all_clients
            
        except Exception as e:
            print(f"クライアント一覧取得エラー: {str(e)}")
            return []
    
    def _is_cache_valid(self) -> bool:
        """キャッシュが有効かどうかを確認"""
        if self._clients_cache is None or self._cache_timestamp is None:
            return False
        
        # キャッシュの有効期限をチェック
        return datetime.now() - self._cache_timestamp < self._cache_duration
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self._clients_cache = None
        self._cache_timestamp = None
        print("クライアントデータのキャッシュをクリア")
    
    async def find_client_by_name(self, client_name: str) -> tuple:
        """クライアント名でクライアントデータベースを検索し、ページIDと略称を返す
        
        キャッシュが利用可能な場合は、キャッシュから検索を行う
        """
        try:
            if not self.notion or not settings.NOTION_CLIENT_DATABASE_ID:
                return None, None
            
            # キャッシュが有効な場合は、キャッシュから検索
            if self._is_cache_valid():
                print(f"キャッシュからクライアントを検索: {client_name}")
                for client in self._clients_cache:
                    if client_name in client["name"]:
                        return client["id"], client["abbreviation"]
                return None, None
            
            # クライアントデータベースを検索
            # タイトルプロパティの場合、プロパティ名ではなく"title"を直接使用
            response = self.notion.databases.query(
                database_id=settings.NOTION_CLIENT_DATABASE_ID,
                filter={
                    "property": "title",  # タイトルプロパティ
                    "title": {
                        "contains": client_name
                    }
                }
            )
            
            if response["results"]:
                client_page = response["results"][0]
                client_id = client_page["id"]
                
                # 略称を取得
                abbreviation = ""
                if "properties" in client_page and "略称" in client_page["properties"]:
                    abbrev_prop = client_page["properties"]["略称"]
                    if abbrev_prop["type"] == "rich_text" and abbrev_prop["rich_text"]:
                        abbreviation = abbrev_prop["rich_text"][0]["text"]["content"]
                
                return client_id, abbreviation
            
            return None, None
            
        except Exception as e:
            print(f"クライアント検索エラー: {str(e)}")
            return None, None

    def generate_title(self, format_category: str, date_value: str, client_abbreviation: str) -> str:
        """タイトルを生成する: 【{OCR結果 - format} {メール取得日時(MM/DD)}】{クライアントテーブルの略称}"""
        try:
            # 日付をMM/DD形式に変換
            date_part = ""
            if date_value:
                try:
                    # ISO 8601形式の日付をパース
                    dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                    date_part = dt.strftime("%m/%d")
                except:
                    date_part = ""
            
            # タイトル構成要素
            format_part = format_category if format_category else ""
            abbrev_part = client_abbreviation if client_abbreviation else ""
            
            # タイトル生成
            if format_part and date_part:
                title = f"【{format_part} {date_part}】{abbrev_part}"
            elif format_part:
                title = f"【{format_part}】{abbrev_part}"
            elif date_part:
                title = f"【{date_part}】{abbrev_part}"
            else:
                title = abbrev_part
            
            return title
            
        except Exception as e:
            print(f"タイトル生成エラー: {str(e)}")
            return ""

    async def create_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Notionデータベースにエントリーを作成"""
        try:
            if not self.notion or not settings.NOTION_DATABASE_ID:
                return {
                    "status": "error",
                    "message": "Notion credentials not configured"
                }
            
            # OCR結果からvendor、content、formatを抽出
            ocr_result = data.get("ocr_result", {})
            vendor = ""
            content = ""
            format_category = ""
            
            if isinstance(ocr_result, dict) and "result" in ocr_result:
                result_data = ocr_result["result"]
                if isinstance(result_data, dict) and "data" in result_data:
                    data_list = result_data["data"]
                    if isinstance(data_list, list) and len(data_list) > 0:
                        first_item = data_list[0]
                        if isinstance(first_item, dict):
                            vendor = first_item.get("vendor", "")
                            content = first_item.get("content", "")
                            format_category = first_item.get("format", "")
            
            # X-API結果からURLを抽出
            x_api_result = data.get("x_api_result", {})
            pdf_url = ""
            
            if isinstance(x_api_result, dict) and "data" in x_api_result:
                x_data = x_api_result["data"]
                if isinstance(x_data, dict) and "data" in x_data:
                    # X-APIの結果は data.data.url の構造になっている
                    inner_data = x_data["data"]
                    if isinstance(inner_data, dict):
                        pdf_url = inner_data.get("url", "")
            
            # 日付フォーマットの変換（ISO 8601形式に変換）
            date_str = data.get("date", "")
            date_value = None
            if date_str:
                try:
                    # メール形式の日付をパース
                    if "," in date_str and ("+" in date_str or "-" in date_str):
                        # RFC 2822形式（例: "Mon, 14 Jul 2025 02:47:14 +0900"）
                        dt = parsedate_to_datetime(date_str)
                        date_value = dt.isoformat()
                    else:
                        # ISO 8601形式の日付文字列をそのまま使用
                        date_value = date_str
                except Exception as e:
                    print(f"日付変換エラー: {e}")
                    date_value = None
            
            # メール情報を取得
            email_subject = data.get("subject", "")
            email_body = data.get("body", "")
            
            # 実際のNotion API呼び出し
            properties = {
                "OCRデータ": {
                    "rich_text": [
                        {
                            "text": {
                                "content": content
                            }
                        }
                    ]
                },
                "ステータス": {
                    "status": {
                        "name": "新規"
                    }
                }
            }
            
            # メール件名プロパティを追加（値がある場合のみ）
            if email_subject:
                properties["メール件名"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": email_subject
                            }
                        }
                    ]
                }
            
            # メール本文プロパティを追加（値がある場合のみ）
            if email_body:
                # Notionのテキストプロパティには文字数制限があるため、必要に応じて切り詰める
                max_length = 2000  # Notionのrich_textプロパティの制限
                truncated_body = email_body[:max_length] if len(email_body) > max_length else email_body
                
                properties["メール本文"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": truncated_body
                            }
                        }
                    ]
                }
            
            # カテゴリープロパティを追加（formatがある場合のみ）
            if format_category:
                properties["カテゴリー"] = {
                    "multi_select": [
                        {
                            "name": format_category
                        }
                    ]
                }
            
            # 日付プロパティを追加（値がある場合のみ）
            if date_value:
                properties["メール取得日時"] = {
                    "date": {
                        "start": date_value
                    }
                }
            
            # クライアント検索・関連付け
            client_id = None
            client_abbreviation = ""
            
            # 曖昧検索結果がある場合は、それを優先的に使用
            fuzzy_search_result = data.get("fuzzy_search_result", {})
            
            # 新しい形式の曖昧検索結果をチェック
            if fuzzy_search_result and "result" in fuzzy_search_result:
                result = fuzzy_search_result["result"]
                if isinstance(result, dict) and result.get("id") != "null":
                    client_id = result.get("id")
                    client_name = result.get("name", "")
                    print(f"曖昧検索で一致したクライアントを使用: {client_name} (ID: {client_id})")
                    
                    # 曖昧検索で見つかったクライアントの略称を取得
                    if client_name:
                        _, client_abbreviation = await self.find_client_by_name(client_name)
                else:
                    print(f"曖昧検索結果: {result.get('name', '該当なし')}")
            elif vendor:
                # 曖昧検索結果がない場合は、従来の検索方法を使用
                client_id, client_abbreviation = await self.find_client_by_name(vendor)
            
            # クライアントが見つかった場合はrelationを追加
            if client_id:
                properties["クライアント"] = {
                    "relation": [
                        {
                            "id": client_id
                        }
                    ]
                }
            
            # PDFのURLがある場合のみ添付PDFプロパティを追加
            if pdf_url:
                properties["添付PDF"] = {
                    "url": pdf_url
                }
            
            # タイトル生成: 【{OCR結果 - format} {メール取得日時(MM/DD)}】{クライアントテーブルの略称}
            title = self.generate_title(format_category, date_value, client_abbreviation)
            if title:
                properties["title"] = {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            
            response = self.notion.pages.create(
                parent={"database_id": settings.NOTION_DATABASE_ID},
                properties=properties
            )
            
            return {
                "status": "success",
                "page_id": response["id"],
                "url": response["url"],
                "message": "Entry created successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Notion entry creation failed: {str(e)}"
            }
