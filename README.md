# CSV Reader

CSV Reader is a FastAPI-based application designed to process CSV files from Google Drive, update a local database with the information, and provide an API to access the product data.

## Features

- Download and process CSV files from Google Drive
- Update SQLite database with CSV data
- Provide a RESTful API to query product information
- Scheduled updates using APScheduler

## Prerequisites

- Python 3.12 or higher
- Poetry for dependency management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/pantech48/csv_reader.git
   cd csv_reader
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Create a `.env` file in the project root and add the following variables:
   ```
   GOOGLE_DRIVE_URL=your_google_drive_url
   CSV_FILE_PATH=path_to_save_csv
   DATABASE_URL=sqlite:///./products.db
   ```

## Usage

To run the application:

```
poetry run app
```

This command will:
1. Process the CSV file from Google Drive and update the database
2. Start the scheduler for periodic updates
3. Launch the FastAPI server on `http://0.0.0.0:8000`

The application will be accessible at `http://localhost:8000`.

## API Endpoints

- `GET /products/`: Retrieve a list of products
  - Query Parameters:
    - `producer` (optional): Filter products by producer
    - `skip` (optional, default=0): Number of records to skip
    - `limit` (optional, default=10, max=100): Number of records to return

## Development

### Running Tests

To run the test suite:

```
poetry run tests
```

### Code Formatting

To format the code using Black:

```
poetry run format
```

### Linting

To run the linter:

```
poetry run lint
```

## Project Structure

- `app/`: Main application package
  - `api.py`: FastAPI route definitions
  - `csv_processor.py`: CSV processing logic
  - `database.py`: Database connection and session management
  - `models.py`: SQLAlchemy model definitions
  - `scheduler.py`: APScheduler setup for periodic updates
- `tests/`: Test files
- `main.py`: Application entry point
- `config.py`: Configuration management
- `pyproject.toml`: Poetry configuration and dependencies

## Scheduled Updates

The application uses APScheduler to periodically update the database with the latest CSV data. The update interval can be configured in the `scheduler.py` file.
