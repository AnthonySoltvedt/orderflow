Research Log – EAS Technical Challenge
Day 1 – 10 November 2026
Project: OrderFlow – Order Monitoring
Objective
Extend my existing OrderFlow application with a monitoring feature that helps small businesses understand their order activity.
Why I chose this project
I previously developed an order automation project and became interested in how businesses can simplify repetitive tasks.
I chose to extend OrderFlow because I wanted to work on a practical problem while improving my backend development and DevOps skills.
Understanding the existing application
Before making changes, I reviewed the existing FastAPI endpoints, PostgreSQL connection logic and authentication system.
I also examined the Git repository and discovered several uncommitted changes. I created a backup and separate development branch before proceeding.
Technical decisions
1. Reusing FastAPI and PostgreSQL
I decided to extend the existing architecture rather than introduce unnecessary technologies.
2. Using SQL aggregation
I implemented a new /orders/summary endpoint using PostgreSQL's COUNT() and GROUP BY functionality.
I chose this approach because it allows the database to calculate order counts without transferring every order into Python.
3. Preserving authentication
The endpoint uses the existing authentication dependency and filters database queries by the authenticated user's ID.
This is important because business users should only access information relating to their own orders.
Challenges encountered
When starting the development server, I encountered an Address already in use error.
I investigated the problem using lsof and identified Python processes listening on port 8000. After resolving the conflict, I successfully restarted Uvicorn.
Testing and results
I tested the new endpoint using FastAPI's Swagger UI.
Unauthenticated request: HTTP 401
Authenticated request: HTTP 200
Response: Order counts grouped by status
The authenticated response contained 11 orders marked Not Started, 2 Printing and 2 Shipped.
What I learned
I gained a better understanding of SQL aggregation, FastAPI route ordering, reusing authentication dependencies and troubleshooting development server port conflicts.
Next steps
Introduce automated testing, improve the monitoring response and explore continuous integration using GitHub Actions.
