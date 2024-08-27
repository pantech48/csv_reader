import uvicorn
from app.api import app
from app.scheduler import start_scheduler
from app.csv_processor import process_csv


def main():
    # Initial data processing
    process_csv()
    # Start the scheduler
    start_scheduler()
    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
