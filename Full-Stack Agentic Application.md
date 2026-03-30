# Full-Stack Agentic Application

This repository contains a complete, functional full-stack application with an Astro frontend, FastAPI backend, PostgreSQL database, JWT authentication, and a switchable agentic framework integration (CrewAI, Agno, LangChain). It is designed to be a production-ready starter kit for building modern web applications with AI capabilities.

## Architecture Overview

For a detailed explanation of the system design, data flow, technology stack, and security considerations, please refer to the [ARCHITECTURE.md](ARCHITECTURE.md) file.

## Features

- **Frontend (Astro)**
  - 3 Pages: Home, CRUD Example, and Agent Interaction
  - Modular component structure
  - REST API integration with TypeScript client
  - Tailwind CSS for styling

- **Backend (FastAPI)**
  - Asynchronous from the ground up
  - Auto-generated OpenAPI documentation (`/docs`)
  - JWT authentication (signup, login, protected routes)
  - CRUD endpoints for item management
  - PostgreSQL integration with Alembic for database migrations

- **Agent Framework**
  - Switchable between **CrewAI**, **Agno**, and **LangChain** via an environment variable.
  - Mock mode for local development without API keys.
  - Agent endpoint (`/agent/query`) for processing user requests.

- **DevOps**
  - Docker Compose setup for a one-command local environment (backend, frontend, database, Redis).
  - GitHub Actions workflow for automated testing and linting.
  - Code quality enforced with `black`, `isort`, and `ruff`.

## Quickstart (Docker Compose)

This is the recommended way to run the project locally. It ensures all services are configured correctly and start in the right order.

**Prerequisites:**
- Docker
- Docker Compose

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd fullstack-agent-app
    ```

2.  **Create environment files:**

    Copy the example environment files. You can customize them later if needed.

    ```bash
    # For the backend
    cp backend/.env.example backend/.env

    # For the frontend
    cp frontend/.env.example frontend/.env
    ```

3.  **Build and run the services:**

    ```bash
    docker compose up --build
    ```

    This command will:
    - Build the Docker images for the frontend and backend.
    - Start the PostgreSQL database and Redis cache.
    - Run database migrations automatically.
    - Start the backend and frontend servers.

4.  **Access the application:**

    - **Frontend:** [http://localhost:4321](http://localhost:4321)
    - **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

## Local Development Setup (Without Docker)

If you prefer to run the services directly on your machine, follow these steps.

**Prerequisites:**
- Python 3.11+
- Node.js 22+ (with `pnpm`)
- PostgreSQL running locally

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**
    - Make sure your PostgreSQL server is running.
    - Create a database named `agentapp`.

5.  **Create the `.env` file:**
    ```bash
    cp .env.example .env
    ```
    Edit `backend/.env` and update `DATABASE_URL` if your PostgreSQL setup is different.

6.  **Run database migrations:**
    ```bash
    alembic upgrade head
    ```

7.  **Run the backend server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The backend will be available at [http://localhost:8000](http://localhost:8000).

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    pnpm install
    ```

3.  **Create the `.env` file:**
    ```bash
    cp .env.example .env
    ```
    The default `PUBLIC_API_URL` points to `http://localhost:8000`, which should work with the local backend setup.

4.  **Run the frontend server:**
    ```bash
    pnpm dev
    ```
    The frontend will be available at [http://localhost:4321](http://localhost:4321).

## Environment Variables

All environment variables are managed in `.env` files. See the `.env.example` files in the `backend` and `frontend` directories for a full list.

### Backend (`backend/.env`)

| Variable                          | Description                                                                                             | Default                                                |
| --------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `DATABASE_URL`                    | Connection string for the PostgreSQL database.                                                          | `postgresql://postgres:postgres@localhost:5432/agentapp` |
| `JWT_SECRET_KEY`                  | Secret key for signing JWT tokens. **Change this in production!**                                         | `your-secret-key-change-in-production`                 |
| `AGENT_FRAMEWORK`                 | The agent framework to use. Options: `crewai`, `agno`, `langchain`.                                       | `crewai`                                               |
| `AGENT_MOCK_MODE`                 | If `True`, the agent will return mock responses instead of using real APIs.                               | `True`                                                 |
| `OPENAI_API_KEY`                  | Your OpenAI API key (only needed if `AGENT_MOCK_MODE` is `False`).                                        | `your-openai-api-key-here`                             |
| `REDIS_URL`                       | Connection string for the Redis cache (optional).                                                       | `redis://localhost:6379/0`                             |

### Frontend (`frontend/.env`)

| Variable         | Description                               | Default                  |
| ---------------- | ----------------------------------------- | ------------------------ |
| `PUBLIC_API_URL` | The base URL of the backend API.          | `http://localhost:8000`  |

## Switching Agent Frameworks

You can easily switch between the integrated agent frameworks by changing the `AGENT_FRAMEWORK` environment variable in the `backend/.env` file or `docker-compose.yml`.

**Supported values:**
- `crewai` (Default)
- `agno`
- `langchain`

After changing the value, restart the backend server or Docker container for the change to take effect.

```env
# Example: Switch to LangChain
AGENT_FRAMEWORK=langchain
```

The application has a fallback mechanism. If the specified framework is not installed or fails to load, it will try the others in the order: `crewai` -> `agno` -> `langchain`.

## Running Tests

Tests are located in the `backend/tests` directory and use `pytest`.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Ensure all test dependencies are installed:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the tests:**
    ```bash
    pytest
    ```

    The tests run against a separate test database and are automatically handled by the GitHub Actions CI workflow.

## Folder Structure

```
fullstack-agent-app/
├── .github/                    # GitHub Actions workflows
├── backend/                    # FastAPI application
│   ├── app/                    # Main application code
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Unit and integration tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Astro application
│   ├── src/                    # Main application code
│   ├── public/                 # Static assets
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # Docker Compose setup
├── ARCHITECTURE.md             # System architecture documentation
└── README.md                   # This file
```

## API Documentation

Once the backend server is running, you can access the interactive OpenAPI documentation at [http://localhost:8000/docs](http://localhost:8000/docs). This interface allows you to explore and test all API endpoints directly from your browser.

## Optional Improvements

This project provides a solid foundation. Here are some suggestions for extending it:

- **Observability**: Integrate distributed tracing with OpenTelemetry and logging with a structured logger like `structlog`.
- **Scaling**: Deploy the application to a cloud provider using Kubernetes or a serverless platform. Use a managed database and Redis instance.
- **Agent Enhancements**: Implement real tool usage for the agents (e.g., web search, database queries). Add a message queue like Celery or RabbitMQ for long-running agent tasks.
- **Frontend State Management**: For more complex state, consider a library like `nanostores` or `preact/signals`.
- **Security**: Implement more robust security measures like rate limiting, more granular permissions, and a Content Security Policy (CSP).
