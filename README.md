# Full-Stack Agentic Application

A complete full-stack application with FastAPI backend, Astro frontend, PostgreSQL database, JWT authentication, and agentic framework integration.

## Project Structure

```
Architecture-Rawah/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routers/        # API routes
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/          # Utilities (auth, dependencies)
│   ├── main.py             # FastAPI app entry point
│   └── requirements.txt    # Python dependencies
├── frontend/               # Astro frontend
│   ├── src/
│   │   ├── pages/          # Astro pages
│   │   ├── layouts/        # Layout components
│   │   └── lib/            # API client
│   └── package.json        # Node.js dependencies
└── docker-compose.yml      # Docker services
```

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 2: Manual Setup

1. **Start PostgreSQL** (required):
   ```bash
   # Using Docker
   docker run -d --name postgres \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=agentapp \
     -p 5432:5432 postgres:15-alpine
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Copy environment file
   cp ../.env.example .env
   
   # Run database migrations
   alembic upgrade head
   
   # Start backend
   python main.py
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Option 3: Quick Test (Python only)

```bash
# Test the backend without database setup
python3 start.py
```

## API Endpoints

- **Health Check**: `GET /health`
- **API Docs**: `GET /docs`
- **Authentication**: 
  - `POST /auth/signup` - User registration
  - `POST /auth/login` - User login
  - `GET /auth/me` - Get current user
- **Items CRUD**: 
  - `GET /items` - List items
  - `POST /items` - Create item
  - `PUT /items/{id}` - Update item
  - `DELETE /items/{id}` - Delete item
- **Agent**: 
  - `POST /agent/query` - Query the agent
  - `GET /agent/status` - Agent status

## Frontend Pages

- **Home**: `http://localhost:4321/`
- **Login**: `http://localhost:4321/login`
- **Signup**: `http://localhost:4321/signup`
- **Items**: `http://localhost:4321/items`
- **Agent**: `http://localhost:4321/agent`

## Configuration

Copy `.env.example` to `.env` and update the values:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agentapp

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-secret-key-here

# Agent Framework (crewai, langchain, agno)
AGENT_FRAMEWORK=crewai
AGENT_MOCK_MODE=True

# OpenAI API (optional)
OPENAI_API_KEY=your-openai-key-here
```

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

Optional landing-page waitlist embed:
- Set `PUBLIC_TALLY_FORM_URL=https://tally.so/r/<your-form-id>` in `frontend/.env`.

### Testing
```bash
cd backend
pytest test_main.py -v
```

## Agent Frameworks

The application supports three agent frameworks:

1. **CrewAI** - Multi-agent orchestration
2. **LangChain** - Comprehensive LLM toolkit
3. **Agno** - Lightweight agent framework

Switch between frameworks using the `AGENT_FRAMEWORK` environment variable.

## Troubleshooting

1. **Database Connection Issues**: Ensure PostgreSQL is running and connection string is correct
2. **Import Errors**: Make sure you're in the correct directory when running commands
3. **Port Conflicts**: Check if ports 8000 (backend) or 4321 (frontend) are already in use
4. **Agent Errors**: Set `AGENT_MOCK_MODE=True` for testing without API keys

## Install Skills (Reliable Method)

If `npx skills add ...` times out for large repositories, use the local helper:

```bash
powershell -ExecutionPolicy Bypass -File scripts/install-skill.ps1 -Skill frontend-design
```

Options:
- `-Repo` (default: `anthropics/skills`)
- `-Experimental` (install from `skills/.experimental/<name>`)
- `-DryRun` (print command without installing)
