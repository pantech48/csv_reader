"""This module contains the scheduler to process the CSV file daily."""

from apscheduler.schedulers.background import BackgroundScheduler

from app.csv_processor import process_csv
from config import SCHEDULER_INTERVAL_DAYS


def start_scheduler() -> None:
    """Start the scheduler to process the CSV file daily."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_csv, "interval", days=SCHEDULER_INTERVAL_DAYS)
    scheduler.start()
