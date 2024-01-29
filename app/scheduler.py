from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

import app.reminders.reminders as rem
from app.utils.utils import reset_chats_answers, remind_later

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


def add_default_jobs(bot):
    scheduler.add_job(rem.brigade_report, trigger='cron', day_of_week='mon-fri', hour='10-23', minute='0,30',
                      start_date=datetime.now(), kwargs={'bot': bot})
    scheduler.add_job(rem.table_update, trigger='cron', day_of_week='thu', hour='11-18/2', start_date=datetime.now(),
                      kwargs={'bot': bot})
    scheduler.add_job(rem.bd_today, trigger='cron', hour=10, minute=10, start_date=datetime.now(),
                      kwargs={'bot': bot})
    scheduler.add_job(rem.new_work, trigger='cron', day_of_week='mon,wed,fri', hour='12-19/2', start_date=datetime.now(),
                      kwargs={'bot': bot})
    scheduler.add_job(reset_chats_answers, trigger='cron', hour=2, minute=0, start_date=datetime.now())


def add_dev_jobs(bot):
    #scheduler.add_job(rem.brigade_report, trigger='cron', minute='*', start_date=datetime.now(), kwargs={'bot': bot})
    #scheduler.add_job(rem.new_work, trigger='cron', minute='*', start_date=datetime.now(),
    #                  kwargs={'bot': bot})
    scheduler.add_job(rem.table_update, trigger='date', run_date=datetime.now() + timedelta(seconds=5), kwargs={'bot': bot})
    # scheduler.add_job(rem.bd_today, trigger='date', run_date=datetime.now() + timedelta(seconds=15), kwargs={'bot': bot})


def add_brigade_planning_reminder(message):
    today = datetime.today()
    if today.hour < 13:
        year = today.year
        month = today.month
        day = today.day
        scheduler.add_job(remind_later, trigger='date', run_date=datetime(year, month, day, hour=13), args=[message])


def start_scheduler():
    scheduler.start()


