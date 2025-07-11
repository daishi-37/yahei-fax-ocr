import asyncio
from app.services.email_service import EmailService


def execute_email_polling_job():
    """メールポーリングジョブを実行"""
    try:
        print("メールポーリングジョブを開始します...")
        
        # 非同期関数を同期的に実行
        email_service = EmailService()
        result = asyncio.run(email_service.poll_emails())
        
        if "error" in result:
            print(f"メールポーリングでエラーが発生しました: {result['error']}")
        else:
            print(f"メールポーリング完了: {result['processed_count']}件のメールを処理しました")
            
    except Exception as e:
        print(f"メールポーリングジョブでエラーが発生しました: {e}")
