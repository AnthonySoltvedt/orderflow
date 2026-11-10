
# Lesson 23: Order Status Workflow

ORDER_STATUSES = [
    "Not Started",
    "Printing",
    "Printed",
    "Shipped"
]


def can_update_status(current_status, new_status):
    # Check both statuses are valid
    if current_status not in ORDER_STATUSES:
        return False

    if new_status not in ORDER_STATUSES:
        return False

    # Find each status position
    current_index = ORDER_STATUSES.index(current_status)
    new_index = ORDER_STATUSES.index(new_status)

    # Only allow moving forward by one stage
    return new_index == current_index + 1


if __name__ == "__main__":
    print(can_update_status("Not Started", "Printing"))
    print(can_update_status("Not Started", "Shipped"))
    print(can_update_status("Printing", "Printed"))
    print(can_update_status("Shipped", "Not Started"))
