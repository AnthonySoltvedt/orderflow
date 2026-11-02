import psycopg

connection = psycopg.connect(
    dbname="orderflow_db",
    user="anthonysoltvedt"
)

print("Successfully connected to PostgreSQL!")

connection.close()