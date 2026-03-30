# Architecture Overview

## System Design

This full-stack application follows a modern three-tier architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT TIER                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Astro Frontend (SSR/SSG)                     │  │
│  │  - Home Page                                         │  │
│  │  - CRUD Example Page (Items Management)             │  │
│  │  - Agent Interaction Page                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                    REST API (JSON)
                            │
┌─────────────────────────────────────────────────────────────┐
│                      APPLICATION TIER                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         FastAPI Backend (Python 3.11+)               │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  Auth Routes (JWT)                             │ │  │
│  │  │  - /auth/signup                                │ │  │
│  │  │  - /auth/login                                 │ │  │
│  │  │  - /auth/me                                    │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  CRUD Routes                                   │ │  │
│  │  │  - /items (GET, POST)                          │ │  │
│  │  │  - /items/{id} (GET, PUT, DELETE)              │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  Agent Routes                                  │ │  │
│  │  │  - /agent/query (POST)                         │ │  │
│  │  │  - /agent/status (GET)                         │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  Agent Framework Layer (Switchable)            │ │  │
│  │  │  - CrewAI (preferred)                          │ │  │
│  │  │  - Agno (fallback 1)                           │ │  │
│  │  │  - LangChain (fallback 2)                      │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                    SQLAlchemy ORM
                            │
┌─────────────────────────────────────────────────────────────┐
│                        DATA TIER                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         PostgreSQL Database                          │  │
│  │  - users table                                       │  │
│  │  - items table                                       │  │
│  │  - agent_logs table (optional)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Redis (Optional - Caching)                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Authentication Flow
1. User submits credentials to `/auth/signup` or `/auth/login`
2. Backend validates credentials and generates JWT token
3. Frontend stores token (localStorage/sessionStorage)
4. Subsequent requests include token in Authorization header
5. Backend middleware validates token and extracts user identity

### CRUD Flow
1. Frontend sends authenticated request to CRUD endpoints
2. Backend validates JWT token
3. SQLAlchemy ORM queries/modifies PostgreSQL database
4. Backend returns JSON response
5. Frontend updates UI reactively

### Agent Interaction Flow
1. User submits query via Agent Interaction page
2. Frontend sends POST request to `/agent/query`
3. Backend routes to appropriate agent framework (CrewAI/Agno/LangChain)
4. Agent processes query using:
   - Tool usage (web search, calculations, etc.)
   - Orchestration logic (multi-step reasoning)
   - LLM integration (OpenAI API or mock mode)
5. Agent returns structured response
6. Backend formats and returns JSON
7. Frontend displays agent response with streaming support (optional)

## Technology Stack

### Frontend
- **Framework**: Astro 4.x
- **Styling**: Tailwind CSS
- **HTTP Client**: Native fetch API
- **State Management**: Astro islands + vanilla JS
- **Build Tool**: Vite (bundled with Astro)

### Backend
- **Framework**: FastAPI 0.110+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Auth**: python-jose (JWT), passlib (password hashing)
- **Validation**: Pydantic v2
- **Testing**: pytest, httpx
- **Code Quality**: black, isort, ruff

### Database
- **Primary**: PostgreSQL 15+
- **Optional Cache**: Redis 7+

### Agent Frameworks
- **Primary**: CrewAI (multi-agent orchestration)
- **Fallback 1**: Agno (lightweight agent framework)
- **Fallback 2**: LangChain (comprehensive agent toolkit)
- **LLM**: OpenAI API (with mock mode for development)

### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Linting/Testing**: Automated in CI pipeline

## Key Design Decisions

### 1. Modular Agent Framework
The `AGENT_FRAMEWORK` environment variable allows switching between CrewAI, Agno, and LangChain without code changes. This provides flexibility for:
- Testing different frameworks
- Migrating between frameworks
- Fallback options if one framework is unavailable

### 2. JWT Authentication
Stateless authentication using JWT tokens enables:
- Scalability (no server-side session storage)
- Microservices compatibility
- Easy integration with mobile apps

### 3. Alembic Migrations
Database schema versioning ensures:
- Reproducible deployments
- Safe schema evolution
- Rollback capability

### 4. Docker Compose
Local development environment includes:
- Backend service
- PostgreSQL database
- Optional Redis cache
- Automatic networking and volume management

### 5. OpenAPI Schema
FastAPI auto-generates OpenAPI documentation at `/docs`, providing:
- Interactive API testing
- Client SDK generation
- API contract validation

## Security Considerations

1. **Password Hashing**: bcrypt via passlib
2. **JWT Secrets**: Environment variable `JWT_SECRET_KEY`
3. **CORS**: Configurable allowed origins
4. **SQL Injection**: Prevented by SQLAlchemy ORM
5. **Input Validation**: Pydantic models on all endpoints
6. **Environment Variables**: Secrets managed via `.env` files (not committed)

## Scalability Path

### Immediate (MVP)
- Single backend instance
- PostgreSQL with connection pooling
- Synchronous agent processing

### Short-term (Growth)
- Redis caching for frequent queries
- Async agent processing with Celery/RQ
- Load balancer (nginx/Traefik)

### Long-term (Scale)
- Kubernetes deployment
- Microservices split (auth, CRUD, agent)
- Message queue (RabbitMQ/Kafka)
- Distributed tracing (OpenTelemetry)
- CDN for frontend assets

## Folder Structure

```
fullstack-agent-app/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API route handlers
│   │   ├── services/          # Business logic
│   │   ├── agents/            # Agent framework integrations
│   │   └── utils/             # Helper functions
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Unit and integration tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                   # Astro application
│   ├── src/
│   │   ├── pages/             # Astro pages
│   │   ├── components/        # Reusable components
│   │   ├── layouts/           # Page layouts
│   │   └── lib/               # Utilities and API client
│   ├── public/                # Static assets
│   ├── astro.config.mjs
│   ├── package.json
│   └── tailwind.config.mjs
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions workflow
├── ARCHITECTURE.md            # This file
└── README.md                  # Setup and usage guide
```

## Next Steps

This architecture document serves as the blueprint for implementation. The following phases will:

1. Build the backend with all specified features
2. Implement agent framework integrations
3. Create the Astro frontend
4. Set up Docker and CI/CD
5. Generate comprehensive documentation
