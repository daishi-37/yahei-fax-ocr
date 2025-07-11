import imaplib
import email
import os
import json
from datetime import datetime
from typing import List, Dict, Any
import aiofiles
from app.core import settings
from app.services.x_api_service import XApiService
from app.services.dify_service import DifyService
from app.services.notion_service import NotionService


class EmailService:
    def __init__(self):
        self.x_api_service = XApiService()
        self.dify_service = DifyService()
        self.notion_service = NotionService()
        
    async def poll_emails(self) -> Dict[str, Any]:
        """メールをポーリングして新しいメールを処理"""
        try:
            # Gmail接続
            mail = imaplib.IMAP4_SSL(settings.GMAIL_IMAP_SERVER, settings.GMAIL_IMAP_PORT)
            mail.login(settings.GMAIL_EMAIL, settings.GMAIL_PASSWORD)
            mail.select('inbox')
            
            # 未読メールを検索
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            processed_emails = []
            
            for email_id in email_ids:
                # メール取得
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # メール情報を抽出
                email_info = await self._extract_email_info(email_message)
                
                # メールファイルを保存
                await self._save_email_file(email_id.decode(), email_message)
                
                # PDF添付ファイルを処理
                pdf_files = await self._process_attachments(email_message, email_id.decode())
                
                # 各PDFファイルを処理
                for pdf_file in pdf_files:
                    # X-APIにアップロード（モック）
                    upload_result = await self.x_api_service.upload_pdf(pdf_file)
                    
                    # DifyでOCR処理（モック）
                    ocr_result = await self.dify_service.process_ocr(pdf_file)
                    
                    # Notionに登録
                    notion_result = await self.notion_service.create_entry({
                        **email_info,
                        "pdf_file": pdf_file,
                        "x_api_result": upload_result,
                        "ocr_result": ocr_result
                    })
                
                processed_emails.append({
                    "email_id": email_id.decode(),
                    "subject": email_info["subject"],
                    "pdf_count": len(pdf_files)
                })
            
            mail.close()
            mail.logout()
            
            return {
                "processed_count": len(processed_emails),
                "emails": processed_emails
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _extract_email_info(self, email_message) -> Dict[str, Any]:
        """メールから情報を抽出"""
        return {
            "subject": email_message.get("Subject", ""),
            "from": email_message.get("From", ""),
            "to": email_message.get("To", ""),
            "date": email_message.get("Date", ""),
            "received_at": datetime.now().isoformat()
        }
    
    async def _save_email_file(self, email_id: str, email_message):
        """メールファイルを保存"""
        os.makedirs(settings.EMAIL_STORAGE_PATH, exist_ok=True)
        
        email_file_path = f"{settings.EMAIL_STORAGE_PATH}/{email_id}.eml"
        
        async with aiofiles.open(email_file_path, 'wb') as f:
            await f.write(email_message.as_bytes())
    
    async def _process_attachments(self, email_message, email_id: str) -> List[str]:
        """添付ファイルを処理してPDFファイルのパスを返す"""
        pdf_files = []
        
        os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
        
        for part in email_message.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename and filename.lower().endswith('.pdf'):
                    # PDFファイルを保存
                    pdf_path = f"{settings.PDF_STORAGE_PATH}/{email_id}_{filename}"
                    
                    async with aiofiles.open(pdf_path, 'wb') as f:
                        await f.write(part.get_payload(decode=True))
                    
                    pdf_files.append(pdf_path)
        
        return pdf_files
    
    async def get_latest_emails(self) -> List[Dict[str, Any]]:
        """最新のメール一覧を取得"""
        emails = []
        
        if os.path.exists(settings.EMAIL_STORAGE_PATH):
            for filename in os.listdir(settings.EMAIL_STORAGE_PATH):
                if filename.endswith('.eml'):
                    email_path = f"{settings.EMAIL_STORAGE_PATH}/{filename}"
                    stat = os.stat(email_path)
                    emails.append({
                        "filename": filename,
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
        
        # 作成日時でソート
        emails.sort(key=lambda x: x["created_at"], reverse=True)
        return emails[:10]  # 最新10件
