## Installation and Testing

### Prerequisites

Before starting, make sure you have installed:

- Python 3.12
- PostgreSQL
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/AnthonySoltvedt/orderflow.git
cd orderflow
git checkout feature/eas-order-monitoring
```

### 2. Create a Python virtual environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it (macOS/Linux):

```bash
source .venv/bin/activate
```

### 3. Install Python dependencies

Install the application and testing dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Set up PostgreSQL

Create a new PostgreSQL database:

```bash
createdb orderflow_db
```

Create the required database tables:

```bash
psql -d orderflow_db -v ON_ERROR_STOP=1 -f schema.sql
```

This creates two tables:

- `users` – stores user accounts and hashed passwords.
- `orders` – stores orders, their statuses and their associated owners.

The schema has been successfully tested against a fresh PostgreSQL database.

**Note:** If `orderflow_db` already exists, do not create it again.

### 5. Configure environment variables

OrderFlow uses environment variables for its database connection and JWT authentication.

Create a local `.env` file using `.env.example` as a reference.

Example:

```dotenv
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:5432/orderflow_db
JWT_SECRET_KEY=REPLACE_WITH_A_SECURE_RANDOM_SECRET_AT_LEAST_48_CHARACTERS
```

Replace these placeholders with your own configuration.

The JWT secret must contain at least 48 characters.

Never commit real credentials or private `.env` files to Git.

### 6. Run automated tests

Execute the Pytest test suite:

```bash
JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')" python -m pytest tests/test_order_summary.py -v
```

This runs four automated tests covering:

1. Authentication requirements.
2. Correct order counts.
3. Statuses with zero orders.
4. Users with no orders.

These tests use mocked database connections, so a running PostgreSQL database is not required for the order summary tests.

The command generates a temporary JWT secret for the test process.

### 7. Start the FastAPI backend

After configuring PostgreSQL and your environment variables, start the backend:

```bash
uvicorn backend.main:app --reload
```

The backend normally runs at:

http://127.0.0.1:8000

FastAPI's interactive API documentation (Swagger UI) is available at:

http://127.0.0.1:8000/docs

Swagger UI can be used to test registration, login, order management and order monitoring.

### 8. Start the React frontend

Open a second terminal in the project directory.

Navigate to the frontend:

```bash
cd frontend
```

Install the JavaScript dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend normally runs at:

http://localhost:5173/

Keep the FastAPI backend running in its separate terminal when using features that require the API.

### Day 3 – Continuous Integration

## Continuous Integration

The GitHub Actions configuration is located at:

`.github/workflows/tests.yml`

The workflow automatically runs the test suite on pushes and pull requests.

This helps detect problems before changes are merged.

## Documentation

- **README.md:** Project overview, features and instructions
- **RESEARCH.md:** Research, technical decisions, development process and lessons learned
- **AI.md:** AI assistance, verification and reflection

## Limitations

The automated tests currently focus on the order monitoring endpoint and use mocked database connections.

They do not provide full integration testing against PostgreSQL or complete coverage of the frontend and other API endpoints.

## Future Improvements

- Add PostgreSQL integration tests
- Expand automated test coverage
- Improve error handling and logging
- Integrate live WooCommerce synchronisation
- Improve frontend monitoring and reporting
- Deploy the application to a cloud platform

## About

Developed by Anthony Soltvedt, an MSc Computer Science with Artificial Intelligence graduate interested in software engineering, automation and DevOps.
