
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")





WOOCOMMERCE_URL = os.getenv("WOOCOMMERCE_URL", "").rstrip("/")
CONSUMER_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
CONSUMER_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "")


def fetch_orders(import_mode=False):
    if not all([WOOCOMMERCE_URL, CONSUMER_KEY, CONSUMER_SECRET]):
        print("WooCommerce settings are missing.")
        return

    endpoint = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/orders"

    response = requests.get(
        endpoint,
        auth=(CONSUMER_KEY, CONSUMER_SECRET),
        params={"per_page": 5},
        timeout=30,
    )

    if response.status_code == 503:
        print("WooCommerce is temporarily unavailable (HTTP 503).")
        print("No orders were fetched or imported. Try again later.")
        return

    if response.status_code == 401:
        print("WooCommerce authentication failed.")
        try:
            error_data = response.json()
            print("Error code:", error_data.get("code", "Unknown"))
            print("Error message:", error_data.get("message", "Unknown"))
        except ValueError:
            print("The server did not return a JSON error.")
        return



    response.raise_for_status()
    orders = response.json()

    if not isinstance(orders, list):
        raise RuntimeError("Unexpected WooCommerce response.")

    print(f"Successfully fetched {len(orders)} orders.")



    for order in orders:
        if not is_eligible_order(order):
            print(f"Order #{order['id']} is not eligible - skipped")
            continue

        transformed = transform_order(order)

        if not validate_order(transformed):
            print(f"Invalid order #{transformed['id']} - skipped")
            continue

        if not import_mode:
            print("IMPORT PREVIEW — no database changes")
        print(f"Order #{transformed['id']}")
        print(f"Production status: {transformed['status']}")
        print(f"Customer name present: {bool(transformed['customer'])}")
        print("---")
        if import_mode:
            import_order(transformed)



def transform_order(order):
    billing = order.get("billing") or {}

    first_name = billing.get("first_name") or ""
    last_name = billing.get("last_name") or ""

    customer = f"{first_name} {last_name}".strip()

    return {
        "id": order["id"],
        "customer": customer,
        "status": "Not Started"
    }


def validate_order(order):
    if type(order.get("id")) is not int or order["id"] <= 0:
        return False

    customer = order.get("customer")
    if not isinstance(customer, str) or not customer.strip():
        return False

    valid_statuses = [
        "Not Started",
        "Printing",
        "Printed",
        "Shipped"
    ]

    if order.get("status") not in valid_statuses:
        return False

    return True

def is_eligible_order(order):
    if order.get("currency") != "GBP":
        return False

    if order.get("status") not in ["processing", "completed"]:
        return False

    if order.get("refunds"):
        return False

    return True


def import_order(order):
    endpoint = "http://127.0.0.1:8000/orders"

    try:
        response = requests.post(
            endpoint,
            json=order,
            timeout=30
        )

        if response.status_code == 201 or response.status_code == 200:
            print(f"Order #{order['id']} imported successfully")

        elif response.status_code == 409:
            print(f"Order #{order['id']} already exists - skipped")

        else:
            print(
                f"Order #{order['id']} failed: "
                f"HTTP {response.status_code}"
            )

    except requests.exceptions.RequestException as error:
        print(f"Could not import order #{order['id']}: {error}")



if __name__ == "__main__":
    import sys

    if "--import" in sys.argv:
        print("IMPORT MODE ENABLED")
        confirmation = input(
            "Type IMPORT to confirm database changes: "
        )

        if confirmation == "IMPORT":
            fetch_orders(import_mode=True)
        else:
            print("Import cancelled.")
    else:
        fetch_orders()
