
from typing import Literal

import psycopg
import os
from psycopg.errors import UniqueViolation

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)
from backend.order_workflow import can_update_status


# APPLICATION

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# DATABASE CONNECTION

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    environment = os.getenv("APP_ENV", "development").lower()

    if database_url:
        return psycopg.connect(database_url)

    if environment == "production":
        raise RuntimeError(
            "DATABASE_URL must be configured in production."
        )

    return psycopg.connect(
        dbname="orderflow_db",
        user="anthonysoltvedt",
    )


# JWT AUTHENTICATION

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> int:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = verify_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE id = %s",
                (user_id,),
            )
            existing_user = cursor.fetchone()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="User account no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


# DATA MODELS

class Order(BaseModel):
    id: int
    customer: str
    status: Literal[
        "Not Started",
        "Printing",
        "Printed",
        "Shipped",
    ]


class StatusUpdate(BaseModel):
    status: Literal[
        "Not Started",
        "Printing",
        "Printed",
        "Shipped",
    ]


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# USER REGISTRATION

@app.post("/register", status_code=201)
def register_user(user: UserRegister):
    email = str(user.email).lower()
    hashed_password = hash_password(user.password)

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (email, password_hash)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (email, hashed_password),
                )
                user_id = cursor.fetchone()[0]

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    return {
        "message": "User registered successfully",
        "user": {
            "id": user_id,
            "email": email,
        },
    }


# USER LOGIN

@app.post("/login")
def login_user(user: UserLogin):
    email = str(user.email).lower()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, password_hash
                FROM users
                WHERE email = %s
                """,
                (email,),
            )
            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    user_id, stored_email, stored_hash = row

    if not verify_password(user.password, stored_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user_id)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": stored_email,
        },
    }


# HOME

@app.get("/")
def home():
    return {"message": "Welcome to OrderFlow"}


# CURRENT AUTHENTICATED USER

@app.get("/me")
def get_my_profile(
    user_id: int = Depends(get_current_user_id),
):
    return {
        "message": "Authentication successful",
        "user_id": user_id,
    }


# ORDER MONITORING - SUMMARY

	# ORDER MONITORING - SUMMARY

@app.get("/orders/summary")
def get_order_summary(
    user_id: int = Depends(get_current_user_id),
):
    # Connect to PostgreSQL
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT status, COUNT(*)
                FROM orders
                WHERE owner_id = %s
                GROUP BY status
                """,
                (user_id,),
            )

            rows = cursor.fetchall()

    # Initialise every order status with zero
    status_counts = {
        "Not Started": 0,
        "Printing": 0,
        "Printed": 0,
        "Shipped": 0,
    }

    # Update counts using the database results
    for status, count in rows:
        status_counts[status] = count

    # Return the summary as JSON
    return {
        "status_counts": status_counts
    }


# GET ALL ORDERS - ONLY THE USER'S OWN ORDERS

@app.get("/orders")
def get_orders(
    user_id: int = Depends(get_current_user_id),
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, customer, status
                FROM orders
                WHERE owner_id = %s
                ORDER BY id
                """,
                (user_id,),
            )
            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "customer": row[1],
            "status": row[2],
        }
        for row in rows
    ]


# GET ONE ORDER - OWNERSHIP REQUIRED

@app.get("/orders/{order_id}")
def get_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, customer, status
                FROM orders
                WHERE id = %s AND owner_id = %s
                """,
                (order_id, user_id),
            )
            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return {
        "id": row[0],
        "customer": row[1],
        "status": row[2],
    }


# CREATE ORDER - AUTOMATIC OWNER ASSIGNMENT

@app.post("/orders")
def create_order(
    order: Order,
    user_id: int = Depends(get_current_user_id),
):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO orders (id, customer, status, owner_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        order.id,
                        order.customer,
                        order.status,
                        user_id,
                    ),
                )

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Order already exists",
        )

    return {
        "message": "Order created",
        "order": order,
    }


# UPDATE ORDER STATUS - OWNERSHIP REQUIRED

@app.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    update: StatusUpdate,
    user_id: int = Depends(get_current_user_id),
):
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT status
                FROM orders
                WHERE id = %s AND owner_id = %s
                FOR UPDATE
                """,
                (order_id, user_id),
            )

            row = cursor.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Order not found",
                )

            current_status = row[0]

            if not can_update_status(
                current_status,
                update.status,
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Cannot change status from "
                        f"{current_status} to {update.status}"
                    ),
                )

            cursor.execute(
                """
                UPDATE orders
                SET status = %s
                WHERE id = %s AND owner_id = %s
                RETURNING id, customer, status
                """,
                (
                    update.status,
                    order_id,
                    user_id,
                ),
            )

            updated_order = cursor.fetchone()

    return {
        "message": "Order status updated",
        "order": {
            "id": updated_order[0],
            "customer": updated_order[1],
            "status": updated_order[2],
        },
    }


# DELETE ORDER - OWNERSHIP REQUIRED

@app.delete("/orders/{order_id}")
def delete_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM orders
                WHERE id = %s AND owner_id = %s
                RETURNING id, customer, status
                """,
                (order_id, user_id),
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return {
        "message": "Order deleted",
        "order": {
            "id": row[0],
            "customer": row[1],
            "status": row[2],
        },
    }
