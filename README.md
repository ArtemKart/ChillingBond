# 🧊 ChillingBond

[![codecov](https://codecov.io/gh/ArtemKart/ChillingBond/branch/main/graph/badge.svg)](https://codecov.io/gh/ArtemKart/ChillingBond)

**Bond Portfolio Management System**

A comprehensive web application for tracking bond investments, calculating yields, and monitoring coupon payments. Built with modern architectural patterns and best development practices.

🌐 **Live Demo:** https://chillingbond.up.railway.app/

---

## ✨ Features

- **Portfolio Management** — Add, edit, and delete bonds in your portfolio
- **BondHolder Tracking** — Track positions with purchase dates and quantities
- **Yield Calculation** — Automatic coupon income calculation using NBP reference rates
- **Authentication** — JWT-based authorization with secure password hashing
- **Responsive UI** — Modern dashboard with sorting and filtering capabilities

---

## 🏗️ Architecture

The project follows **Domain-Driven Design (DDD)** principles with **Hexagonal Architecture** (Ports & Adapters):

```
src/
├── domain/                 # Core business logic
│   ├── entities/           # User, Bond, BondHolder, Portfolio
│   ├── value_objects/      # Email, ReferenceRate
│   ├── ports/              # Interfaces (ABC) for external dependencies
│   ├── services/           # Domain services (BondMaturityChecker)
│   ├── events/             # Domain events
│   └── exceptions/         # Business exceptions
│
├── application/            # Application layer
│   ├── use_cases/          # Business operations (CRUD, calculations)
│   ├── dto/                # Data Transfer Objects
│   └── events/             # Event handlers
│
└── adapters/               # Adapters
    ├── inbound/            # API (FastAPI endpoints)
    │   ├── api/            # REST API
    │   └── scheduler/      # Scheduled tasks
    └── outbound/           # External services
        ├── database/       # PostgreSQL + SQLAlchemy
        ├── repositories/   # Repository implementations
        └── security/       # bcrypt, JWT

frontend/                   # Next.js application
├── app/                    # App Router (pages)
├── components/             # React components
├── lib/                    # API client
└── types/                  # TypeScript types
```

---

## 🛠️ Tech Stack

### Backend
| Technology         | Purpose              |
|--------------------|----------------------|
| **Python 3.12**    | Programming language |
| **FastAPI**        | Async web framework  |
| **SQLAlchemy 2.0** | Async ORM            |
| **PostgreSQL**     | Database             |
| **Alembic**        | Database migrations  |
| **Pydantic**       | Data validation      |
| **bcrypt**         | Password hashing     |
| **PyJWT**          | JWT tokens           |
| **uv**             | Package manager      |

### Frontend
| Technology       | Purpose         |
|------------------|-----------------|
| **Next.js 14**   | React framework |
| **TypeScript**   | Type safety     |
| **Tailwind CSS** | Styling         |
| **shadcn/ui**    | UI components   |

### Infrastructure
| Technology             | Purpose          |
|------------------------|------------------|
| **Docker**             | Containerization |
| **Nginx**              | Reverse proxy    |
| **Gunicorn + Uvicorn** | WSGI/ASGI server |
| **Railway**            | Hosting          |
| **GitHub Actions**     | CI/CD            |

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ArtemKart/ChillingBond.git
   cd ChillingBond
   ```

2. **Create `.env` file:**
   ```bash
   cp .env-template .env
   ```

3. **Configure environment variables in `.env`:**
   ```env
    # example
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=postgres
    
    # Application User (CRUD operations)
    DB_APP_USER=application_user
    DB_APP_PASSWORD=secure_passsword
    
    # Migration User (DDL operations)
    DB_MIGRATION_USER=migration_user
    DB_MIGRATION_PASSWORD=secure_password
    
    DRIVER=postgresql+asyncpg
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    
    ENVIRONMENT=dev
    SECRET_KEY=secret_key
   ```

4. **Start the application:**
   ```bash
   docker compose up -d --build
   ```

5. **Migrations will automatically apply in dedicated container**

6. **Open in browser:**
   - Application: [http://localhost](http://localhost)
   - API Documentation: [http://localhost/api/docs](http://localhost/api/docs)

---

## 💻 Local Development

### Backend
Before you start working with backend locally, ensure you expose postgres container ports.
```yaml
services:
  database:
    ports:
      - "5432:5432"
```
Before synchronizing project dependencies, ensure `uv` is installed (otherwise install it using the guide: [link](https://docs.astral.sh/uv/getting-started/installation/))
```bash
>>> uv --help
An extremely fast Python package manager.

Usage: uv [OPTIONS] <COMMAND>

Commands:
  auth     Manage authentication
  run      Run a command or script
  init     Create a new project
  add      Add dependencies to the project
  remove   Remove dependencies from the project
  version  Read or update the project's version
  sync     Update the project's environment
  lock     Update the project's lockfile
  export   Export the project's lockfile to an alternate format
  tree     Display the project's dependency tree
  format   Format Python code in the project
  tool     Run and install commands provided by Python packages
  python   Manage Python versions and installations
  pip      Manage Python packages with a pip-compatible interface
  venv     Create a virtual environment
  build    Build Python packages into source distributions and wheels
  publish  Upload distributions to an index
  cache    Manage uv's cache
  self     Manage the uv executable
  help     Display documentation for a command
```
Once you ensure 
```bash
cd ChillingBond

# Install dependencies
uv sync

# Start PostgreSQL and apply migrations
docker compose up -d --build database migrations

# Start development server on uvicorn
uv run python -m src.adapters.inbound.api.start_api
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Tests

#### Unit tests
```bash
uv run pytest tests/unit -v
```

#### Integration tests
Integration tests run against a real database in a test Docker container
using testcontainers. This may take several minutes to complete.
```bash
uv run pytest tests/integration -v
```

#### Load tests (Locust)
Before running load tests, create `.env.locust` file:
```bash
cp /tests/load/.env.locust-template .env.locust
```
You may leave variables' values as it is. It will work properly.

```bash
# run sh script to configure environment
./tests/load/run_load_test.sh
```
Now, open the link: http://localhost:8089/ and set new load test parameters.


---

## 📚 API Endpoints

### Authentication
| Method | Endpoint           | Description                  |
|--------|--------------------|------------------------------|
| POST   | `/api/login/token` | Set cookie with JWT token    |
| GET    | `/api/login/me`    | Get user UUID by its token   |
| POST   | `/api/logout`      | Delete JWT token from cookie |

### User
| Method | Endpoint          | Description             |
|--------|-------------------|-------------------------|
| POST   | `/api/users`      | Create user             |
| GET    | `/api/users/{id}` | Get user by its UUID    |
| DELETE | `/api/users/{id}` | Delete user by its UUID |



### BondHolders
| Method | Endpoint                         | Description                |
|--------|----------------------------------|----------------------------|
| POST   | `/api/bonds`                     | Create a bondholder        |
| GET    | `/api/bonds`                     | List all bondholders       |
| GET    | `/api/bonds/{id}`                | Get bondholder by id       |
| PATCH  | `api/bonds/{id}/quantity`        | Change bondholder quantity |
| PUT    | `/api/bonds/{id}/specification"` | Update bond specification  |
| DELETE | `/api/bonds/{id}`                | Delete bondholder          |


### Calculations
| Method | Endpoint                         | Description               |
|--------|----------------------------------|---------------------------|
| POST   | `/api/calculations/month-income` | Calculate position income |

Full API documentation available at `/api/docs` (Swagger UI).

---

## 🔧 Configuration

### Docker Compose Services

| Service     | Port | Description      |
|-------------|------|------------------|
| `nginx`     | 80   | Reverse proxy    |
| `backend`   | 8000 | FastAPI API      |
| `frontend`  | 3000 | Next.js app      |
| `database`  | 5432 | PostgreSQL       |
| `scheduler` | -    | Background tasks |


---

## 🗂️ Project Structure

```
ChillingBond/
├── src/                    # Backend source code
│   ├── domain/             # Business logic layer
│   ├── application/        # Application layer
│   └── adapters/           # Infrastructure layer
├── frontend/               # Next.js frontend
├── tests/                  # Test suites
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── load/               # Load tests
├── alembic.ini             # Database migrations configuration
├── nginx/                  # Reverse proxy setup
├── dockerfiles/            # Dockerfiles
├── docker-compose.yml      # Docker configuration
├── logging.yml             # Logging configuration
└── pyproject.toml          # Python dependencies
```

---

## 🧪 Testing Strategy

The project uses a multi-layered testing approach:

- **Unit Tests** — Domain entities and services with mocked dependencies
- **Integration Tests** — Use cases with real database connections
- **Load Tests** — Performance testing with Locust
---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Python: Follow PEP 8, use type hints, pre-commit hooks
- Commits: Conventional commits format
---

## 👤 Author

**Artem Kartashov** -- GitHub: [@ArtemKart](https://github.com/ArtemKart), email: artem_kartashov@icloud.com

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [Next.js](https://nextjs.org/) — React framework for production
- [Railway](https://railway.app/) — Simple cloud hosting
- [NBP API](https://api.nbp.pl/) — Polish National Bank reference rates
