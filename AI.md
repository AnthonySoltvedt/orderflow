# AI Usage – OrderFlow Technical Challenge

## Purpose

This document explains how I used AI assistance during the Enterprise Automation Services technical challenge and how I verified the suggestions provided.

## How I used AI

I used ChatGPT as a learning and development assistant to help me understand unfamiliar concepts, plan development tasks, troubleshoot errors and review code.

Rather than treating AI-generated suggestions as automatically correct, I ran the commands myself, examined the results and made changes based on the evidence.

## Day 1 – API Development

AI helped me understand how to add an authenticated order-monitoring endpoint using FastAPI and PostgreSQL.

We discussed SQL aggregation, authentication dependencies, route ordering and how to organise the changes using Git.

I verified the endpoint manually through Swagger UI, checking that unauthenticated requests returned HTTP 401 and authenticated requests returned the expected order counts.

## Day 2 – Automated Testing

AI helped me learn Pytest, mocking and Test-Driven Development.

I used AI-generated examples of fake database connections and test cases, then ran them locally.

Some tests initially failed because the expected results did not match the intended response or the supplied mock data. I investigated those differences and corrected the assertions.

I also refactored duplicated test code into reusable components.

All four tests passed locally.

## Day 3 – Continuous Integration

AI guided me through creating a GitHub Actions workflow to automate the test suite.

The first CI run failed because the backend required a JWT secret key that was not available in GitHub's environment.

I examined the workflow logs and identified the missing environment variable.

With AI assistance, I updated the workflow to use a dummy test-only JWT secret rather than my production secret.

The next workflow run completed successfully.

## How I verified AI suggestions

I verified suggestions by:

- Running code and commands locally.
- Testing API behaviour through Swagger UI.
- Running automated tests using Pytest.
- Inspecting Git changes before committing.
- Reviewing GitHub Actions logs when the pipeline failed.
- Checking that local environment files were ignored by Git.

## Limitations and future improvements

The current automated tests use a mocked database. They do not replace PostgreSQL integration tests.

The testing environment also produces a Starlette deprecation warning that should be investigated.

I intend to continue improving test coverage, dependency management and the application's reliability.

## Reflection

AI accelerated my learning, particularly when working with unfamiliar testing and DevOps tools.

The most valuable part of the process was investigating failures and understanding why solutions worked, rather than simply copying code.

I remain responsible for reviewing, testing and understanding the code submitted.