# Local RAG System

A local RAG system using OpenAI, pgvector, and Streamlit.

## Setup

1.  **Prerequisites**:
    *   Python 3.10+
    *   PostgreSQL with `vector` extension installed.
        *   Windows: Use the installer from [pgvector](https://github.com/pgvector/pgvector) or run via Docker.
        *   Ensure you can connect to your Postgres instance.

2.  **Environment Variables**:
    *   Copy `.env` template: `cp .env.example .env` (if I created one, otherwise just edit `.env`)
    *   Edit `.env`:
        ```
        OPENAI_API_KEY=sk-...
        POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/rag_db
        ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the App

```bash
streamlit run src/app.py
```

## Features

*   **Document Ingestion**: PDF, DOCX, TXT, MD, HTML.
*   **Vector Store**: Persistent storage using `pgvector`.
*   **Retrieval**: Hybrid retrieval with adjacency (fetching surrounding chunks for context).
*   **Chat**: Interactive chat with citations and debug view.
