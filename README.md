# ai_email_responder
This is an email responder application that fetches unread emails, classifies them using AI, and sends automated responses. The application can be run inside a Docker container or on a local machine.

## Features
- Fetches unread emails from a configured email account
- Uses Relevance AI to classify email intent and generate responses
- Sends automated responses via SMTP
- Logs responses to a local SQLite database
- Provides an API endpoint to manually trigger email processing

## Directory Structure
project-root/
├── src/
│   ├── email_responder.py  # Main script
│   └── credentials.yml     # Email credentials
├── data/
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # Documentation

## Setup & Installation

### Running Inside Docker

1.  **Build and start the Docker container:**

    ```bash
    docker-compose up --build
    ```

2.  **Run the FastAPI server inside the container:**

    ```bash
    uvicorn email_responder:app --host 0.0.0.0 --port 8000 --reload
    ```

3.  **To manually trigger email processing, run the following command inside the container:**

    ```bash
    curl -X POST http://localhost:8000/process_emails
    ```

    * This can be later automated as per the need.

### Running Outside Docker

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the FastAPI server:**

    ```bash
    uvicorn email_responder:app --host 0.0.0.0 --port 8000 --reload
    ```

3.  **Manually trigger email processing:**

    ```bash
    curl -X POST http://localhost:8000/process_emails
    ```

## API Endpoints

* `POST /process_emails` - Triggers the email processing workflow.
* `GET /responses` - Fetches logged email responses.

## Notes

* Ensure you configure `credentials.yml` with the correct email settings.
* Modify the AI classification logic as per your requirements.
* This application can be run outside the Docker environment as well.
