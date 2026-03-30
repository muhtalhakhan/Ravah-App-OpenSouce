# Quickstart Guide

This guide will help you get the full-stack agent application running on your local machine in under 5 minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)

To verify your installations, run:

```bash
docker --version
docker compose version
```

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fullstack-agent-app
```

### 2. Set Up Environment Variables

Create the environment files from the provided examples:

```bash
# Backend environment
cp backend/.env.example backend/.env

# Frontend environment
cp frontend/.env.example frontend/.env
```

**Note:** The default configuration uses mock mode for the agent, so you don't need an OpenAI API key to get started.

### 3. Start the Application

Run the following command to build and start all services:

```bash
docker compose up --build
```

This command will:
- Build Docker images for the backend and frontend
- Start PostgreSQL database
- Start Redis cache
- Run database migrations automatically
- Start the backend API server
- Start the frontend development server

The first build may take a few minutes. Subsequent starts will be much faster.

### 4. Access the Application

Once all services are running, you can access:

- **Frontend:** [http://localhost:4321](http://localhost:4321)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

## First Steps

### Create an Account

1. Navigate to [http://localhost:4321/signup](http://localhost:4321/signup)
2. Fill in the registration form:
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `password123`
3. Click "Sign Up"
4. You'll be redirected to the login page

### Log In

1. Navigate to [http://localhost:4321/login](http://localhost:4321/login)
2. Enter your credentials:
   - Username: `testuser`
   - Password: `password123`
3. Click "Login"
4. You'll be redirected to the Items page

### Try the CRUD Features

1. Click "Create Item" to add a new item
2. Fill in the title and description
3. Click "Save"
4. Try editing and deleting items

### Interact with the Agent

1. Navigate to the "Agent" page from the navigation menu
2. Enter a question in the text area (e.g., "What is the weather like today?")
3. Click "Send Query"
4. View the agent's response

The agent is running in **mock mode** by default, so responses are simulated. To use a real agent framework with OpenAI:

1. Edit `backend/.env`
2. Set `AGENT_MOCK_MODE=False`
3. Set `OPENAI_API_KEY=your-actual-api-key`
4. Restart the backend: `docker compose restart backend`

## Stopping the Application

To stop all services:

```bash
docker compose down
```

To stop and remove all data (database, volumes):

```bash
docker compose down -v
```

## Troubleshooting

### Port Already in Use

If you see an error like "port is already allocated", another service is using one of the required ports (4321, 8000, 5432, or 6379). Either stop the conflicting service or modify the port mappings in `docker-compose.yml`.

### Database Connection Errors

If the backend fails to connect to the database, ensure PostgreSQL is healthy:

```bash
docker compose ps
```

All services should show as "healthy" or "running". If not, check the logs:

```bash
docker compose logs postgres
docker compose logs backend
```

### Frontend Not Loading

If the frontend shows a blank page, check the browser console for errors. Ensure the `PUBLIC_API_URL` in `frontend/.env` matches your backend URL.

## Next Steps

- Explore the [README.md](README.md) for detailed documentation
- Read the [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
- Check out the [API documentation](http://localhost:8000/docs) to see all available endpoints
- Modify the code and see live changes (hot reload is enabled)

## Switching Agent Frameworks

To switch between CrewAI, Agno, and LangChain:

1. Edit `backend/.env`
2. Change `AGENT_FRAMEWORK` to `crewai`, `agno`, or `langchain`
3. Restart the backend: `docker compose restart backend`

The application will automatically use the specified framework.

## Running Tests

To run the backend tests:

```bash
# Enter the backend container
docker compose exec backend bash

# Run tests
pytest

# Exit the container
exit
```

Alternatively, run tests without entering the container:

```bash
docker compose exec backend pytest
```

---

**Congratulations!** You now have a fully functional full-stack application with AI agent integration running locally.
