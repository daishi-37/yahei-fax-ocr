from fastapi import APIRouter
from app.services.email_service import EmailService
from app.core import settings
import os
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()
email_service = EmailService()

@router.get("/status")
async def get_email_status():
    """メールポーリングの状態を取得"""
    return {"status": "running", "message": "Email polling system is active"}

@router.post("/poll")
async def manual_poll_emails():
    """手動でメールポーリングを実行"""
    result = await email_service.poll_emails()
    return {"message": "Email polling completed", "result": result}

@router.get("/latest")
async def get_latest_emails():
    """最新のメール一覧を取得"""
    emails = await email_service.get_latest_emails()
    return {"emails": emails}

@router.get("/processed-ids")
async def get_processed_ids():
    """処理済みメールID情報を取得"""
    info = await email_service.get_processed_ids_info()
    return info

@router.delete("/processed-ids")
async def clear_processed_ids():
    """処理済みメールIDをクリア（管理用）"""
    result = await email_service.clear_processed_ids()
    return result

@router.delete("/storage/cleanup")
async def cleanup_storage(days_old: Optional[int] = 7):
    """古いストレージファイルをクリーンアップ
    
    Args:
        days_old: 何日以上前のファイルを削除するか（デフォルト: 7日）
    """
    try:
        deleted_files = {
            "emails": [],
            "pdfs": []
        }
        
        cutoff_time = datetime.now() - timedelta(days=days_old)
        
        # メールファイルのクリーンアップ
        if os.path.exists(settings.EMAIL_STORAGE_PATH):
            for filename in os.listdir(settings.EMAIL_STORAGE_PATH):
                if filename.endswith('.eml'):
                    file_path = os.path.join(settings.EMAIL_STORAGE_PATH, filename)
                    file_stat = os.stat(file_path)
                    file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    if file_mtime < cutoff_time:
                        os.remove(file_path)
                        deleted_files["emails"].append({
                            "filename": filename,
                            "modified_time": file_mtime.isoformat()
                        })
        
        # PDFファイルのクリーンアップ
        if os.path.exists(settings.PDF_STORAGE_PATH):
            for filename in os.listdir(settings.PDF_STORAGE_PATH):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(settings.PDF_STORAGE_PATH, filename)
                    file_stat = os.stat(file_path)
                    file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    if file_mtime < cutoff_time:
                        os.remove(file_path)
                        deleted_files["pdfs"].append({
                            "filename": filename,
                            "modified_time": file_mtime.isoformat()
                        })
        
        return {
            "message": f"{days_old}日以上前のファイルを削除しました",
            "deleted_count": {
                "emails": len(deleted_files["emails"]),
                "pdfs": len(deleted_files["pdfs"])
            },
            "deleted_files": deleted_files
        }
        
    except Exception as e:
        return {"error": f"ストレージクリーンアップエラー: {str(e)}"}

@router.get("/storage/stats")
async def get_storage_stats():
    """ストレージの統計情報を取得"""
    try:
        stats = {
            "emails": {
                "count": 0,
                "total_size": 0
            },
            "pdfs": {
                "count": 0,
                "total_size": 0
            }
        }
        
        # メールファイルの統計
        if os.path.exists(settings.EMAIL_STORAGE_PATH):
            for filename in os.listdir(settings.EMAIL_STORAGE_PATH):
                if filename.endswith('.eml'):
                    file_path = os.path.join(settings.EMAIL_STORAGE_PATH, filename)
                    file_stat = os.stat(file_path)
                    stats["emails"]["count"] += 1
                    stats["emails"]["total_size"] += file_stat.st_size
        
        # PDFファイルの統計
        if os.path.exists(settings.PDF_STORAGE_PATH):
            for filename in os.listdir(settings.PDF_STORAGE_PATH):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(settings.PDF_STORAGE_PATH, filename)
                    file_stat = os.stat(file_path)
                    stats["pdfs"]["count"] += 1
                    stats["pdfs"]["total_size"] += file_stat.st_size
        
        # バイトをMBに変換
        stats["emails"]["total_size_mb"] = round(stats["emails"]["total_size"] / (1024 * 1024), 2)
        stats["pdfs"]["total_size_mb"] = round(stats["pdfs"]["total_size"] / (1024 * 1024), 2)
        stats["total_size_mb"] = round((stats["emails"]["total_size"] + stats["pdfs"]["total_size"]) / (1024 * 1024), 2)
        
        return stats
        
    except Exception as e:
        return {"error": f"ストレージ統計取得エラー: {str(e)}"}
