from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
import psycopg

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


class Order(BaseModel):
    id: int
    customer: str
    status: str

class StatusUpdate(BaseModel):
    status: Literal["Not Started", "Printing", "Printed", "Shipped"]


orders = [
    {"id": 1001, "customer": "James", "status": "Printing"},
    {"id": 1002, "customer": "Sarah", "status": "Not Started"},
    {"id": 1003, "customer": "Michael", "status": "Shipped"}
]


@app.get("/")
def home():
    return {"message": "Welcome to OrderFlow"}


@app.get("/orders")
def get_orders():
    with psycopg.connect(
        dbname="orderflow_db",
        user="anthonysoltvedt"
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, customer, status FROM orders"
            )

            rows = cursor.fetchall()

    return [
        {"id": row[0], "customer": row[1], "status": row[2]}
        for row in rows
    ]


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    with psycopg.connect(
        dbname="orderflow_db",
        user="anthonysoltvedt"
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, customer, status
                FROM orders
                WHERE id = %s
                """,
                (order_id,)
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return {
        "id": row[0],
        "customer": row[1],
        "status": row[2]
    }

    for order in orders:
        if order["id"] == order_id:
            return order

    raise HTTPException(
        status_code=404,
        detail="Order not found"
    )




@app.post("/orders")
def create_order(order: Order):
    try:
        with psycopg.connect(
            dbname="orderflow_db",
            user="anthonysoltvedt"
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO orders (id, customer, status)
                    VALUES (%s, %s, %s)
                    """,
                    (order.id, order.customer, order.status)
                )

        return {
            "message": "Order created",
            "order": order
        }

    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Order already exists"
        )

    for existing_order in orders:
        if existing_order["id"] == order.id:
            raise HTTPException(
                status_code=409,
                detail="Order already exists"
            )

    orders.append(order.model_dump())

    return {"message": "Order created", "order": order}


@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, update: StatusUpdate):
    with psycopg.connect(
        dbname="orderflow_db",
        user="anthonysoltvedt"
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE orders
                SET status = %s
                WHERE id = %s
                RETURNING id, customer, status
                """,
                (update.status, order_id)
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return {
        "message": "Order status updated",
        "order": {
            "id": row[0],
            "customer": row[1],
            "status": row[2]
        }
    }

    for order in orders:
        if order["id"] == order_id:
            order["status"] = update.status
            return {
                "message": "Order status updated",
                "order": order
            }

    raise HTTPException(
        status_code=404,
        detail="Order not found"
    )



@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    with psycopg.connect(
        dbname="orderflow_db",
        user="anthonysoltvedt"
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM orders
                WHERE id = %s
                RETURNING id, customer, status
                """,
                (order_id,)
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return {
        "message": "Order deleted",
        "order": {
            "id": row[0],
            "customer": row[1],
            "status": row[2]
        }
    }

    for order in orders:
        if order["id"] == order_id:
            orders.remove(order)

            return {
                "message": "Order deleted",
                "order": order
            }

    raise HTTPException(
        status_code=404,
        detail="Order not found"
    )
