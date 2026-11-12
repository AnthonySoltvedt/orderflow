# OrderFlow

**A full-stack order management and monitoring application built using Python, FastAPI, PostgreSQL and React.**

## Overview

OrderFlow is a software development project designed to explore how businesses can manage orders more efficiently through software and automation.

The application allows authenticated users to manage their orders, track order statuses and retrieve a summary showing how many orders are at each stage.

For the Enterprise Automation Services technical challenge, I extended my existing OrderFlow project by introducing order monitoring, automated testing and a Continuous Integration (CI) pipeline.

## The Problem

Businesses managing multiple orders need a simple way to understand their workload.

Without a clear overview, it can be difficult to see how many orders are waiting to be processed, currently in production or ready for dispatch.

OrderFlow addresses this by providing an API that organises and summarises order information.

## Technologies

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **Frontend:** React, JavaScript
- **Authentication:** JWT and Argon2 password hashing
- **Automated testing:** Pytest, FastAPI TestClient
- **Continuous Integration:** GitHub Actions
- **Version control:** Git and GitHub

## Features

### Order Management

- Create and retrieve orders
- Update order statuses
- Delete orders
- Store order information in PostgreSQL
- Associate orders with authenticated users

### Authentication

- User registration and login
- JWT-based authentication
- Password hashing
- Protected API endpoints

### Order Monitoring

The monitoring API allows authenticated users to view their order counts by status.

**Endpoint:** `GET /orders/summary`

Example response:

```json
{
  "status_counts": {
    "Not Started": 3,
    "Printing": 2,
    "Printed": 0,
    "Shipped": 1
  }
}
```

The endpoint groups orders by status and returns zero counts for statuses without matching orders.

The database query filters orders by the authenticated user's ID.

### WooCommerce Automation

- Process sample WooCommerce order data
- Extract and store order information
- Prevent duplicate orders during processing

## Technical Challenge Development

### Day 1 – API Development

Added an authenticated order monitoring endpoint using FastAPI and PostgreSQL.

Tested the endpoint manually using Swagger UI.

### Day 2 – Automated Testing

Introduced Pytest to verify the order monitoring feature.

Created four automated tests covering:

1. Authentication requirements
2. Correct order counts
3. Missing statuses
4. Users with no orders

Used mocked database connections to isolate tests from the real PostgreSQL database.

Practised Test-Driven Development using the Red–Green–Refactor approach.

### Day 3 – Continuous Integration

Implemented a GitHub Actions workflow that automatically runs checks when code is pushed or a pull request is opened.

The workflow:

1. Checks out the repository
2. Installs Python 3.12
3. Installs the development dependencies
4. Checks Python syntax
5. Runs the automated tests

The first CI run failed because a required JWT environment variable was missing.

After investigating the workflow logs, I configured a test-only JWT secret. The subsequent workflow completed successfully.

## Installation and Testing

### Prerequisites

- Python 3.12
- PostgreSQL for database-backed application features
- Node.js and npm for the React frontend

### 1. Clone the repository

```bash
git clone https://github.com/AnthonySoltvedt/orderflow.git
cd orderflow
git checkout feature/eas-order-monitoring
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install development dependencies

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Configure environment variables

Use `.env.example` as a reference for the required environment variables.

The backend requires a PostgreSQL connection string and a JWT secret of at least 48 characters.

Do not commit real credentials or private environment files.

### 5. Run the automated tests

```bash
python -m pytest tests/test_order_summary.py -v
```

The four order summary tests use mocked database responses and do not require a running PostgreSQL server, provided the required application environment configuration is supplied.

### 6. Start the backend

After configuring PostgreSQL and the necessary environment variables:

```bash
uvicorn backend.main:app --reload
```

FastAPI's interactive API documentation is available at:

`http://127.0.0.1:8000/docs`

A PostgreSQL database with the application's required tables must be configured before using the database-backed endpoints.

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
