
# Lesson 19: Simulated WooCommerce orders

from woocommerce_client import (
    transform_order,
    validate_order,
    is_eligible_order,
    import_order
)


# Step 1: Create simulated WooCommerce orders
def fetch_mock_orders():
    orders = [
        {
            "id": 3001,
            "status": "processing",
            "currency": "GBP",
            "refunds": [],
            "billing": {
                "first_name": "Emma",
                "last_name": "Wilson"
            }
        },
        {
            "id": 3002,
            "status": "completed",
            "currency": "GBP",
            "refunds": [],
            "billing": {
                "first_name": "Oliver",
                "last_name": "Brown"
            }
        },
        {
            "id": 3003,
            "status": "processing",
            "currency": "GBP",
            "refunds": [],
            "billing": {
                "first_name": "Sophia",
                "last_name": "Taylor"
            }
        }
    ]

    return orders


# Step 2: Process and synchronise orders
def sync_mock_orders(import_mode=False):
    orders = fetch_mock_orders()

    print(f"Found {len(orders)} simulated orders.")

    for order in orders:

        # Check whether the order is eligible
        if not is_eligible_order(order):
            print(f"Order #{order['id']} not eligible - skipped")
            continue

        # Transform WooCommerce data into OrderFlow format
        transformed = transform_order(order)

        # Validate the transformed order
        if not validate_order(transformed):
            print(f"Order #{order['id']} invalid - skipped")
            continue

        # Import or preview the order
        if import_mode:
            import_order(transformed)
        else:
            print(f"PREVIEW: Order #{transformed['id']} ready to sync")

    print("Synchronisation finished.")


# Step 3: Run the simulation in preview mode
if __name__ == "__main__":
    sync_mock_orders(import_mode=True)
