import json
import urllib.request
import urllib.error
# Sample WooCommerce orders
# These are fake orders for testing our integration.

sample_orders = [
    {
        "id": 2001,
        "status": "processing",
        "billing": {
            "first_name": "James",
            "last_name": "Smith"
        }
    },
    {
        "id": 2002,
        "status": "processing",
        "billing": {
            "first_name": "Sarah",
            "last_name": "Jones"
        }
    },
    {
        "id": 2003,
        "status": "completed",
        "billing": {
            "first_name": "Michael",
            "last_name": "Brown"
        }
    }
]

# Print each order to test the data

# Convert WooCommerce orders into OrderFlow format

for order in sample_orders:
    order_id = order["id"]

    first_name = order["billing"]["first_name"]
    last_name = order["billing"]["last_name"]

    customer = first_name + " " + last_name

    # Every imported order starts as Not Started
    production_status = "Not Started"

    orderflow_order = {
        "id": order_id,
        "customer": customer,
        "status": production_status
    }

    print(orderflow_order)



# Send an order to our FastAPI backend

def validate_order(order):
    if not isinstance(order.get("id"), int) or isinstance(order.get("id"), bool) or order["id"] <= 0:
        print("Invalid order ID")
        return False

    customer = order.get("customer")
    if not isinstance(customer, str) or not customer.strip():
        print("Customer name is missing")
        return False

    if order.get("status") not in [
        "Not Started",
        "Printing",
        "Printed",
        "Shipped"
    ]:
        print("Invalid order status")
        return False

    return True


def import_order(order):
    # Check the order before importing
    if not validate_order(order):
        print(f"Skipping invalid order: {order}")
        return

    url = "http://127.0.0.1:8000/orders"


    data = json.dumps(order).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            print(f"Imported order #{order['id']}")

    except urllib.error.HTTPError as error:
        if error.code == 409:
            print(f"Skipped duplicate order #{order['id']}")
        else:
            print(f"Failed to import order #{order['id']}: {error.code}")


# Import all three sample orders
for order in sample_orders:
    orderflow_order = {
        "id": order["id"],
        "customer": (
            order["billing"]["first_name"]
            + " "
            + order["billing"]["last_name"]
        ),
        "status": "Not Started"
    }

    import_order(orderflow_order)
