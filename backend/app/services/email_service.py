import imaplib
import email
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Set
import aiofiles
from email.header import decode_header
from app.core import settings


class EmailService:
    def __init__(self):
        self.processed_ids_file = f"{settings.STORAGE_PATH}/processed_email_ids.json"
        self.last_poll_time_file = f"{settings.STORAGE_PATH}/last_poll_time.json"
    
    def _decode_mime_words(self, s):
        """MIME エンコードされた文字列をデコード"""
        if not s:
            return ""
        
        decoded_parts = []
        for part, encoding in decode_header(s):
            if isinstance(part, bytes):
                if encoding:
                    try:
                        decoded_parts.append(part.decode(encoding))
                    except (UnicodeDecodeError, LookupError):
                        # エンコーディングが不明な場合はUTF-8で試す
                        try:
                            decoded_parts.append(part.decode('utf-8'))
                        except UnicodeDecodeError:
                            # それでもダメな場合はエラーを無視
                            decoded_parts.append(part.decode('utf-8', errors='ignore'))
                else:
                    # エンコーディングが指定されていない場合
                    try:
                        decoded_parts.append(part.decode('utf-8'))
                    except UnicodeDecodeError:
                        decoded_parts.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded_parts.append(str(part))
        
        return ''.join(decoded_parts)
    
    async def _load_processed_ids(self) -> Set[str]:
        """処理済みメールIDを読み込み"""
        try:
            if os.path.exists(self.processed_ids_file):
                async with aiofiles.open(self.processed_ids_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    return set(data.get('processed_ids', []))
            return set()
        except Exception as e:
            print(f"処理済みID読み込みエラー: {e}")
            return set()
    
    async def _save_processed_ids(self, processed_ids: Set[str]):
        """処理済みメールIDを保存"""
        try:
            os.makedirs(settings.STORAGE_PATH, exist_ok=True)
            data = {
                'processed_ids': list(processed_ids),
                'last_updated': datetime.now().isoformat()
            }
            async with aiofiles.open(self.processed_ids_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            print(f"処理済みID保存エラー: {e}")
    
    async def _add_processed_id(self, email_id: str):
        """処理済みIDを追加"""
        processed_ids = await self._load_processed_ids()
        processed_ids.add(email_id)
        await self._save_processed_ids(processed_ids)
    
    async def _load_last_poll_time(self) -> datetime:
        """前回のポーリング時刻を読み込み"""
        try:
            if os.path.exists(self.last_poll_time_file):
                async with aiofiles.open(self.last_poll_time_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    return datetime.fromisoformat(data.get('last_poll_time'))
            # 初回実行時は24時間前から開始
            from datetime import timedelta
            return datetime.now() - timedelta(hours=24)
        except Exception as e:
            print(f"前回ポーリング時刻読み込みエラー: {e}")
            from datetime import timedelta
            return datetime.now() - timedelta(hours=24)
    
    async def _save_last_poll_time(self, poll_time: datetime):
        """前回のポーリング時刻を保存"""
        try:
            os.makedirs(settings.STORAGE_PATH, exist_ok=True)
            data = {
                'last_poll_time': poll_time.isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            async with aiofiles.open(self.last_poll_time_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            print(f"前回ポーリング時刻保存エラー: {e}")
        
    async def poll_emails(self) -> Dict[str, Any]:
        """メールをポーリングして新しいメールを処理"""
        try:
            current_time = datetime.now()
            
            # 前回のポーリング時刻を読み込み
            last_poll_time = await self._load_last_poll_time()
            
            # 処理済みIDを読み込み
            processed_ids = await self._load_processed_ids()
            
            # Gmail接続
            mail = imaplib.IMAP4_SSL(settings.GMAIL_IMAP_SERVER, settings.GMAIL_IMAP_PORT)
            mail.login(settings.GMAIL_EMAIL, settings.GMAIL_PASSWORD)
            mail.select('inbox')
            
            # 前回のポーリング時刻以降のメールを検索
            # IMAPの日付フォーマット: DD-MMM-YYYY (例: 01-Jan-2024)
            since_date = last_poll_time.strftime("%d-%b-%Y")
            print(f"前回ポーリング時刻: {last_poll_time.isoformat()}")
            print(f"検索条件: SINCE {since_date}")
            
            status, messages = mail.search(None, f'SINCE {since_date}')
            email_ids = messages[0].split()
            
            # 最新から古い順に並び替え
            email_ids.reverse()
            
            print(f"検索結果: {len(email_ids)}件のメールが見つかりました")
            
            processed_emails = []
            skipped_emails = []
            consecutive_processed_count = 0
            
            for email_id in email_ids:
                email_id_str = email_id.decode()
                
                # 既に処理済みかチェック
                if email_id_str in processed_ids:
                    consecutive_processed_count += 1
                    skipped_emails.append({
                        "email_id": email_id_str,
                        "reason": "already_processed"
                    })
                    print(f"メールID {email_id_str} は既に処理済みのためスキップします")
                    
                    # 連続して10件処理済みメールが見つかったら、それより古いメールは処理済みと判断して終了
                    if consecutive_processed_count >= 10:
                        print("連続して10件の処理済みメールが見つかったため、ポーリングを終了します")
                        break
                    
                    continue
                
                # 新しいメールが見つかったら連続カウントをリセット
                consecutive_processed_count = 0
                
                # メール取得
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # メール情報を抽出
                email_info = await self._extract_email_info(email_message)
                
                # メールファイルを保存
                await self._save_email_file(email_id_str, email_message)
                
                # PDF添付ファイルを処理
                pdf_files = await self._process_attachments(email_message, email_id_str)
                
                # 処理済みIDとして記録
                await self._add_processed_id(email_id_str)
                
                processed_emails.append({
                    "email_id": email_id_str,
                    "subject": email_info["subject"],
                    "from": email_info["from"],
                    "date": email_info["date"],
                    "pdf_files": pdf_files,
                    "email_info": email_info
                })
                
                print(f"メールID {email_id_str} の処理が完了しました")
            
            mail.close()
            mail.logout()
            
            # ポーリング完了時刻を保存
            await self._save_last_poll_time(current_time)
            
            return {
                "processed_count": len(processed_emails),
                "skipped_count": len(skipped_emails),
                "emails": processed_emails,
                "skipped_emails": skipped_emails,
                "poll_time_range": {
                    "from": last_poll_time.isoformat(),
                    "to": current_time.isoformat()
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _extract_email_info(self, email_message) -> Dict[str, Any]:
        """メールから情報を抽出"""
        # MIMEエンコードされた文字列をデコード
        subject_raw = email_message.get("Subject", "")
        from_raw = email_message.get("From", "")
        to_raw = email_message.get("To", "")
        
        # メール本文を抽出
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # テキスト部分を抽出（添付ファイルは除外）
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body_part = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body = body_part.decode(charset, errors='ignore')
                        break  # プレーンテキストが見つかったら終了
                    except Exception as e:
                        print(f"メール本文デコードエラー: {e}")
        else:
            # シングルパートメッセージの場合
            try:
                body_part = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset() or 'utf-8'
                body = body_part.decode(charset, errors='ignore')
            except Exception as e:
                print(f"メール本文デコードエラー: {e}")
        
        return {
            "subject": self._decode_mime_words(subject_raw),
            "from": self._decode_mime_words(from_raw),
            "to": self._decode_mime_words(to_raw),
            "date": email_message.get("Date", ""),
            "body": body,
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
    
    async def get_processed_ids_info(self) -> Dict[str, Any]:
        """処理済みID情報を取得"""
        try:
            if os.path.exists(self.processed_ids_file):
                async with aiofiles.open(self.processed_ids_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    return {
                        "total_processed": len(data.get('processed_ids', [])),
                        "last_updated": data.get('last_updated', ''),
                        "processed_ids": data.get('processed_ids', [])
                    }
            return {
                "total_processed": 0,
                "last_updated": '',
                "processed_ids": []
            }
        except Exception as e:
            return {"error": f"処理済みID情報取得エラー: {str(e)}"}
    
    async def clear_processed_ids(self) -> Dict[str, Any]:
        """処理済みIDをクリア（管理用）"""
        try:
            if os.path.exists(self.processed_ids_file):
                os.remove(self.processed_ids_file)
            return {"message": "処理済みIDをクリアしました"}
        except Exception as e:
            return {"error": f"処理済みIDクリアエラー: {str(e)}"}
