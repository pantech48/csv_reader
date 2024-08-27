from apscheduler.schedulers.background import BackgroundScheduler
from .csv_processor import process_csv

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_csv, 'interval', days=1)
    scheduler.start()