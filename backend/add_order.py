import psycopg

connection = psycopg.connect(
    dbname="orderflow_db",
    user="anthonysoltvedt"
)

cursor = connection.cursor()

cursor.execute(
    """
    INSERT INTO orders (id, customer, status)
    VALUES (%s, %s, %s)
    """,
    (1001, "James", "Printing")
)

connection.commit()

print("Order saved successfully!")

cursor.close()
connection.close()