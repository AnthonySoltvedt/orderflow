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

## Day 2 – 11 November 2026

### Objective

Introduce automated testing to improve the reliability and maintainability of the OrderFlow monitoring feature.

### Why I chose Pytest

I wanted to move beyond manually testing API endpoints through Swagger UI and introduce repeatable checks that could detect regressions as the application develops.

I chose Pytest because it supports straightforward assertions, reusable fixtures and mocking, and can be integrated into automated CI pipelines.

### Mocking the database

I used fake database connections and cursors to test the order monitoring endpoint without modifying the real PostgreSQL database.

This allowed me to provide predictable order counts and verify that the API returned the expected results.

### Test-Driven Development

I practised the Red–Green–Refactor approach when improving how the endpoint handles order statuses.

**Red:** I wrote a test expecting all four statuses to appear, including those with zero orders. The test initially failed because the endpoint omitted statuses that had no matching database records.

**Green:** I updated the endpoint to initialise all four statuses to zero before applying the database results. The new test passed.

**Refactor:** I noticed duplicated fake database code in my tests, so I extracted it into reusable classes and a helper function.

### Challenges encountered

After changing the endpoint's response format, an earlier test failed because its expected output no longer matched the intended behaviour.

I also accidentally changed the expected Printing count in another test. I compared the mocked input data, expected output and actual output to identify and correct both assertions.

### Testing results

Four automated tests passed:

- Requests without authentication return HTTP 401.
- Authenticated requests return the expected counts using mocked data.
- All four order statuses appear in the response.
- Users with no orders receive zero counts for every status.

### Further investigation

The testing environment produced a Starlette deprecation warning related to HTTPX. The tests still passed, but I plan to investigate dependency compatibility.

I also recognise that mocked tests do not replace integration tests against PostgreSQL.

### What I learned

I developed a stronger understanding of automated testing, mocking, regression testing, edge cases and Test-Driven Development.

I also learned that test failures require investigation rather than simply changing assertions to make them pass.

## Day 3 – 12 November 2026

### Objective

Introduce Continuous Integration using GitHub Actions so that OrderFlow's automated tests run whenever code is pushed to GitHub.

### Why I chose GitHub Actions

GitHub Actions integrates directly with my Git repository and allows me to automate software testing without manually running commands on my local computer.

### Implementation

I created `.github/workflows/tests.yml` to configure an automated workflow that:

- Runs when code is pushed or a pull request is opened.
- Uses a GitHub-hosted Linux environment.
- Installs Python 3.12 and project dependencies.
- Checks Python syntax.
- Executes the automated Pytest test suite.

### Challenge encountered

The first workflow failed during test collection because the application's JWT secret key was missing in GitHub's environment.

Although the tests worked locally, GitHub Actions did not have access to the environment variables stored on my development machine.

### Solution

I investigated the workflow logs and identified the missing `JWT_SECRET_KEY`.

I configured a dummy test-only JWT key for the Pytest step rather than exposing my real secret.

After committing and pushing this change, the second workflow run completed successfully.

### What I learned

I learned how Continuous Integration works, how to configure GitHub Actions and how to investigate failures using workflow logs.

I also developed a better understanding of environment variables and why software can behave differently between local and remote environments.

The workflow now provides automated feedback whenever changes are pushed to the repository.

## Day 4 – 13 November 2026

### Objective

Verify that OrderFlow works correctly beyond mocked automated tests by testing the real application against PostgreSQL.

### Testing performed

I confirmed that all four Pytest tests passed locally, the React frontend built successfully and Oxlint reported no errors or warnings.

I then performed an end-to-end API test using FastAPI's Swagger UI.

I registered a new test account, logged in and verified JWT authentication using `GET /me`.

Next, I created order `90001` with the status `Not Started`. The order-monitoring endpoint correctly returned one order in that status.

I updated the order to `Printing` using the status update endpoint.

When I requested the summary again, it correctly returned zero `Not Started` orders and one `Printing` order.

### Results

The test confirmed that authentication, order creation, database persistence, status updates and order monitoring work together.

### What I learned

I learned the difference between tests using mocked dependencies and end-to-end API testing against a real database.

I also gained experience validating a complete user workflow and checking that a database change is correctly reflected in an API response.

### Limitations

The React user interface was not included in this end-to-end test. Testing with a second authenticated user would also provide stronger evidence of data isolation.
