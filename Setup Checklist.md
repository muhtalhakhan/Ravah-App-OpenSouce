# Setup Checklist

Use this checklist to ensure you have completed all necessary steps to get the application running.

## Prerequisites

- [ ] Docker installed (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] Git installed

**For local development (optional):**
- [ ] Python 3.11+ installed
- [ ] Node.js 22+ installed
- [ ] pnpm installed (`npm install -g pnpm`)
- [ ] PostgreSQL running locally

## Initial Setup

- [ ] Clone the repository
- [ ] Navigate to the project directory (`cd fullstack-agent-app`)
- [ ] Copy `backend/.env.example` to `backend/.env`
- [ ] Copy `frontend/.env.example` to `frontend/.env`

## Configuration (Optional)

- [ ] Review `backend/.env` and update if needed
- [ ] Review `frontend/.env` and update if needed
- [ ] If using real OpenAI API:
  - [ ] Set `AGENT_MOCK_MODE=False` in `backend/.env`
  - [ ] Set `OPENAI_API_KEY=your-actual-key` in `backend/.env`
- [ ] If changing agent framework:
  - [ ] Set `AGENT_FRAMEWORK=crewai|agno|langchain` in `backend/.env`

## Running with Docker Compose

- [ ] Run `docker compose up --build`
- [ ] Wait for all services to start (may take a few minutes on first run)
- [ ] Verify all services are healthy: `docker compose ps`
- [ ] Access frontend at http://localhost:4321
- [ ] Access backend at http://localhost:8000
- [ ] Access API docs at http://localhost:8000/docs

## Testing the Application

- [ ] Navigate to http://localhost:4321/signup
- [ ] Create a test account
- [ ] Log in with your credentials
- [ ] Create a new item on the Items page
- [ ] Edit and delete an item
- [ ] Navigate to the Agent page
- [ ] Send a query to the agent
- [ ] Verify the agent responds

## Running Tests

- [ ] Run `docker compose exec backend pytest`
- [ ] Verify all tests pass

## Local Development Setup (Optional)

### Backend
- [ ] Create Python virtual environment
- [ ] Install dependencies (`pip install -r backend/requirements.txt`)
- [ ] Run migrations (`alembic upgrade head`)
- [ ] Start backend server (`uvicorn app.main:app --reload`)
- [ ] Verify backend is running at http://localhost:8000

### Frontend
- [ ] Install dependencies (`pnpm install`)
- [ ] Start frontend server (`pnpm dev`)
- [ ] Verify frontend is running at http://localhost:4321

## Troubleshooting

If you encounter issues:

- [ ] Check Docker logs: `docker compose logs`
- [ ] Check specific service logs: `docker compose logs backend` or `docker compose logs frontend`
- [ ] Verify ports are not in use: `lsof -i :4321,8000,5432,6379`
- [ ] Restart services: `docker compose restart`
- [ ] Rebuild images: `docker compose up --build`
- [ ] Remove all containers and volumes: `docker compose down -v`

## Next Steps

Once everything is working:

- [ ] Read the [README.md](README.md) for detailed documentation
- [ ] Review the [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
- [ ] Explore the API documentation at http://localhost:8000/docs
- [ ] Customize the application for your use case
- [ ] Set up a Git repository for version control
- [ ] Configure CI/CD with GitHub Actions

## Production Deployment Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False` in backend
- [ ] Use a managed PostgreSQL database
- [ ] Set up proper environment variable management (e.g., AWS Secrets Manager)
- [ ] Configure CORS origins for your production domain
- [ ] Set up SSL/TLS certificates
- [ ] Configure a reverse proxy (nginx, Traefik)
- [ ] Set up monitoring and logging
- [ ] Configure backups for the database
- [ ] Set up a CDN for frontend assets
- [ ] Implement rate limiting
- [ ] Review and update security settings

---

**Congratulations!** If you've checked all the boxes, your application is ready to use.
