from notion_client import Client
from typing import Dict, Any
from app.core import settings


class NotionService:
    """Notion API連携サービス"""
    
    def __init__(self):
        if settings.NOTION_TOKEN:
            self.notion = Client(auth=settings.NOTION_TOKEN)
        else:
            self.notion = None
    
    async def create_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Notionデータベースにエントリーを作成"""
        try:
            if not self.notion or not settings.NOTION_DATABASE_ID:
                # モック実装
                return {
                    "status": "success",
                    "page_id": f"mock_page_id_{data.get('subject', 'unknown')}",
                    "url": f"https://notion.so/mock_page_id",
                    "message": "Entry created successfully (mock - Notion credentials not configured)"
                }
            
            # 実際のNotion API呼び出し
            properties = {
                "Subject": {
                    "title": [
                        {
                            "text": {
                                "content": data.get("subject", "No Subject")
                            }
                        }
                    ]
                },
                "From": {
                    "rich_text": [
                        {
                            "text": {
                                "content": data.get("from", "")
                            }
                        }
                    ]
                },
                "Date": {
                    "rich_text": [
                        {
                            "text": {
                                "content": data.get("date", "")
                            }
                        }
                    ]
                },
                "PDF File": {
                    "rich_text": [
                        {
                            "text": {
                                "content": data.get("pdf_file", "")
                            }
                        }
                    ]
                },
                "OCR Result": {
                    "rich_text": [
                        {
                            "text": {
                                "content": str(data.get("ocr_result", {}))
                            }
                        }
                    ]
                },
                "X-API Result": {
                    "rich_text": [
                        {
                            "text": {
                                "content": str(data.get("x_api_result", {}))
                            }
                        }
                    ]
                }
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
