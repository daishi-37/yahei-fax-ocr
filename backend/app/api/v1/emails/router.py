from fastapi import APIRouter
from app.services.email_service import EmailService

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
