# AI-Powered Document Intelligence System

A high-performance REST API service that extracts text from images (receipts/invoices) using **EasyOCR**, stores structured data in **SQLite**, and enables natural language Q&A using **Groq**.

The system is built with **FastAPI** for high throughput, uses **EasyOCR** with GPU acceleration support for text extraction, and leverages **Groq** for ultra-low latency LLM responses.

---

## Directory Structure

```plaintext
.
├── app
│   ├── api.py              # FastAPI endpoints for upload and Q&A
│   ├── database.py         # SQLite database models and CRUD operations
│   ├── llm.py              # Groq LLM integration for Q&A
│   ├── main.py             # FastAPI app initialization
│   ├── ocr.py              # OCR preprocessing and text extraction logic
│   └── schemas.py          # Pydantic models for request and response validation
├── tests
│   └── test.py             # Unit tests
├── usage.py                # Example script to simulate user workflow
├── Dockerfile              # Dockerfile for containerization
├── docker-compose.yml      # Docker Compose configuration
├── uv.lock                 # Lock file for dependencies
├── pyproject.toml          # Project metadata and dependencies
└── requirements.txt        # Requirements file
```


## 1. Architecture Overview

The system follows a modular, layered architecture designed for scalability and maintainability:

* **API Layer (`app/api.py`, `app/main.py`)**:
    * Built with **FastAPI**.
    * Handles HTTP requests, input validation, and routing.
    * Implements **asynchronous** endpoints to handle high concurrency.

* **Service Layer**:
    * **OCR Service (`app/ocr.py`)**:
        * Preprocessing pipeline: Grayscale conversion, FFT blur detection, and adaptive sharpening.
        * Uses **EasyOCR** for robust text extraction.
    * **LLM Service (`app/llm.py`)**:
        * Integrates with **Groq** as the LLM backend.
        * Constructs prompts using retrieval-augmented generation (RAG) principles (Context + Question).

* **Data Layer (`app/database.py`)**:
    * **SQLite** for lightweight, serverless persistence.
    * **SQLAlchemy ORM** for database interactions.
    * Stores document metadata, extracted text, and unique content hashes (MD5) to prevent duplicate uploads.

* **Testing & Client**:
    * **`test.py`**: Comprehensive unit tests using `pytest`.
    * **`usage.py`**: A simulation script for end-to-end user workflows.

---

## 2. Model & Library Choices

| Component | Choice | Reasoning |
| :--- | :--- | :--- |
| **Framework** | **FastAPI** | Selected for its asynchronous capabilities (crucial for I/O bound LLM calls), automatic OpenAPI documentation, and high performance compared to Flask/Django. |
| **OCR Engine** | **EasyOCR** | Chosen over Tesseract for better accuracy on diverse layouts and GPU acceleration support. It runs locally, ensuring data privacy before LLM transmission. |
| **LLM Provider** | **Groq** | Chosen for LPU architecture which provides inference at near-instant speeds. Essential for real-time Q&A where latency is critical. |
| **Database** | **SQLite** | Chosen for simplicity and ease of containerization. It removes the need for a separate database container while handling the project's data scale effectively. |
| **Package Manager** | **uv** | Used instead of pip for extremely fast dependency resolution and installation, significantly speeding up build times. |

---

## 3. Completed Features

* **Smart Ingestion Pipeline**:
    * Accepts image uploads via REST API.
    * **Preprocessing**: Automatically detects blurry images and applies sharpening filters.
    * **Duplicate Detection**: Computes MD5 hashes of file content to prevent redundant processing and storage.
* **Text Extraction (OCR)**:
    * Robust extraction of text from receipts and invoices using EasyOCR.
    * Optimized configuration (`detail=0`) for speed.
    * Uses GPU acceleration when available.
* **Natural Language Q&A**:
    * Retrieves document context based on ID.
    * Answers user questions using the Llama-3.3-70b-versatile model via Groq.
* **System Reliability**:
    * **Asynchronous Processing**: OCR runs in thread pools; LLM calls are async.
    * **Health Checks**: `/health` endpoint for monitoring.
    * **Error Handling**: Comprehensive try/catch blocks with meaningful HTTP exceptions.
* **Dockerization**
    * Dockerfile for easy deployment in containerized environments.
    * Lightweight image optimized for fast startup and low resource usage.
* **Testing & Tooling**:
    * Full `pytest` suite covering API endpoints, database logic, and mocking external services.
    * Interactive script (`usage.py`) for easy demonstration.

---


## 4. Future Improvements

With more time, the system could be improved by:

1.  **Vector Search (RAG)**: Instead of passing *all* extracted text to the LLM (which might hit token limits), chunk the text, store embeddings in a vector DB (like Chroma), and retrieve only relevant chunks for the question.
2.  **Frontend Dashboard**: Build a simple React/Streamlit UI to visualize uploaded receipts and chat with them.
3.  **Incorporating Citations**: Use vector search to provide source citations in LLM answers by referencing document chunks.

---

## How to Run

### Prerequisites
* Python 3.10+
* Docker (optional, for containerized deployment)
* Groq API Key

### Installation
1.  **Install uv** (if not already installed):

-   Windows - Open PowerShell in administrator mode and run:
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

-   macOS/Linux
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd AI-Powered-Document-Intelligence-System
    ```

3.  **Install dependencies**:
    ```bash
    uv sync
    ```

4.  **Environment Variables**:
    Create a `.env` file in the root directory with the following content:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    ```

### Running the Application
1.  **Start the FastAPI server**:
    ```bash
    python -m app.main
    ```

The API will be accessible at `http://localhost:8000/`.

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Running Example usage

In a separate terminal, run the usage script to simulate uploading a document and asking a question:

```bash
uv run usage.py
```

### Docker Deployment

1.  **Build the Docker image**:
    ```bash
    docker build -t doc-intel .
    ```

2.  **Run the Docker container**:
    ```bash
    docker run --gpus all \
    -p 8000:8000 \
    -e GROQ_API_KEY="your_key_here" \
    -v "$(pwd)/doc_intel.db:/app/doc_intel.db" \
    doc-intel
    ```

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **OCR**: EasyOCR
- **LLM**: Groq (Llama-3.3-70b-versatile)
- **Database**: SQLite, SQLAlchemy
- **Package Management**: uv

