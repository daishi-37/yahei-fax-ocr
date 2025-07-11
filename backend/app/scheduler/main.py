from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

from app.core import settings
from app.scheduler.jobs.email_polling_job import execute_email_polling_job

scheduler = BackgroundScheduler(
    job_defaults={
        'coalesce': True,
        'max_instances': 1
    }
)


def start_scheduler():
    try:
        if scheduler.running:
            print("スケジューラーは既に実行中です")
            return

        # メールポーリングジョブ
        scheduler.add_job(
            func=execute_email_polling_job,
            trigger=IntervalTrigger(minutes=settings.EMAIL_POLLING_INTERVAL_MINUTES),
            id='email_polling_job',
            name='Email Polling Job',
            max_instances=1,
            replace_existing=True
        )

        scheduler.start()
        print(f"スケジューラーを開始しました")
        print(f"メールポーリング間隔: {settings.EMAIL_POLLING_INTERVAL_MINUTES}分")

        atexit.register(lambda: scheduler.shutdown() if scheduler.running else None)

    except Exception as e:
        print(f"スケジューラーの開始でエラーが発生しました: {e}")


def stop_scheduler():
    try:
        if scheduler.running:
            scheduler.shutdown()
            print("スケジューラーを停止しました")
    except Exception as e:
        print(f"スケジューラーの停止でエラーが発生しました: {e}")
