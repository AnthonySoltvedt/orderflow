
import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  // React state
  const [orders, setOrders] = useState([]);
  const [newOrderId, setNewOrderId] = useState("");
  const [newCustomer, setNewCustomer] = useState("");
  const [newStatus, setNewStatus] = useState("Not Started");
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [sortBy, setSortBy] = useState("newest");

  // READ: Load orders from FastAPI
  useEffect(() => {
    fetch(`${API_URL}/orders`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load orders");
        }
        return response.json();
      })
      .then((data) => setOrders(data))
      .catch((error) => {
        console.error(error);
        alert("Failed to load orders. Check that FastAPI is running.");
      });
  }, []);

  // UPDATE: Change an order's status
  async function updateStatus(orderId, newStatus) {
    try {
      const response = await fetch(
        `${API_URL}/orders/${orderId}/status`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update order");
      }

      setOrders((previousOrders) =>
        previousOrders.map((order) =>
          order.id === orderId
            ? { ...order, status: newStatus }
            : order
        )
      );
    } catch (error) {
      console.error(error);
      alert("Failed to update order");
    }
  }

  // CREATE: Add a new order
  async function addOrder(event) {
    event.preventDefault();

    const newOrder = {
      id: Number(newOrderId),
      customer: newCustomer.trim(),
      status: newStatus,
    };

    if (!Number.isInteger(newOrder.id) ||
        newOrder.id <= 0 ||
        !newOrder.customer) {
      alert("Please enter a valid Order ID and customer name");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/orders`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newOrder),
      });

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error("This Order ID already exists");
        }
        throw new Error("Failed to add order");
      }

      // Refresh orders from PostgreSQL
      const ordersResponse = await fetch(`${API_URL}/orders`);

      if (!ordersResponse.ok) {
        throw new Error("Order saved, but failed to refresh orders");
      }

      const updatedOrders = await ordersResponse.json();
      setOrders(updatedOrders);

      // Clear form
      setNewOrderId("");
      setNewCustomer("");
      setNewStatus("Not Started");
    } catch (error) {
      console.error(error);
      alert(error.message);
    }
  }

  // DELETE: Remove an order
  async function deleteOrder(orderId) {
    const confirmed = window.confirm(
      `Are you sure you want to delete order #${orderId}?`
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/orders/${orderId}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete order");
      }

      // Remove deleted order from dashboard
      setOrders((previousOrders) =>
        previousOrders.filter((order) => order.id !== orderId)
      );
    } catch (error) {
      console.error(error);
      alert("Failed to delete order");
    }
  }

  return (
    <div>
      <h1>OrderFlow Dashboard</h1>
      <p>Welcome to your order management system.</p>

      {/* Dashboard Summary Cards */}
      <div className="summary-container">
        <div className="summary-card">
          <h3>Total Orders</h3>
          <p>{orders.length}</p>
        </div>

        <div className="summary-card">
          <h3>Not Started</h3>
          <p>
            {
              orders.filter(
                (order) => order.status === "Not Started"
              ).length
            }
          </p>
        </div>

        <div className="summary-card">
          <h3>Printing</h3>
          <p>
            {
              orders.filter(
                (order) => order.status === "Printing"
              ).length
            }
          </p>
        </div>

        <div className="summary-card">
          <h3>Printed</h3>
          <p>
            {
              orders.filter(
                (order) => order.status === "Printed"
              ).length
            }
          </p>
        </div>

        <div className="summary-card">
          <h3>Shipped</h3>
          <p>
            {
              orders.filter(
                (order) => order.status === "Shipped"
              ).length
            }
          </p>
        </div>
      </div>

      {/* Add New Order Form */}
      <div className="order-form">
        <h2>Add New Order</h2>

        <form onSubmit={addOrder}>
          <input
            type="number"
            min="1"
            step="1"
            placeholder="Order ID"
            value={newOrderId}
            onChange={(event) =>
              setNewOrderId(event.target.value)
            }
            required
          />

          <input
            type="text"
            placeholder="Customer Name"
            value={newCustomer}
            onChange={(event) =>
              setNewCustomer(event.target.value)
            }
            required
          />

          <select
            value={newStatus}
            onChange={(event) =>
              setNewStatus(event.target.value)
            }
          >
            <option value="Not Started">Not Started</option>
            <option value="Printing">Printing</option>
            <option value="Printed">Printed</option>
            <option value="Shipped">Shipped</option>
          </select>

          <button type="submit">Add Order</button>
        </form>
      </div>

      {/* Customer Orders Table */}



{/* Customer Orders Table */}
<h2>Customer Orders</h2>

<div className="order-filters">
  <input
    type="text"
    placeholder="Search customer or order ID..."
    value={searchTerm}
    onChange={(event) => setSearchTerm(event.target.value)}
  />


<select
  value={statusFilter}
  onChange={(event) => setStatusFilter(event.target.value)}
>
  <option value="All">All Statuses</option>
  <option value="Not Started">Not Started</option>
  <option value="Printing">Printing</option>
  <option value="Printed">Printed</option>
  <option value="Shipped">Shipped</option>
</select>

{/* NEW: Sorting Dropdown */}
<select
  value={sortBy}
  onChange={(event) => setSortBy(event.target.value)}
>
  <option value="newest">Newest First</option>
  <option value="oldest">Oldest First</option>
  <option value="name">Customer A-Z</option>
  <option value="status">Status A-Z</option>
</select>

</div>


<table>

  <thead>
          <tr>
            <th>Order ID</th>
            <th>Customer</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>


{orders
  .filter((order) => {
    const matchesSearch =
      order.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(order.id).includes(searchTerm);

    const matchesStatus =
      statusFilter === "All" || order.status === statusFilter;

    return matchesSearch && matchesStatus;

  })
  .sort((a, b) => {
    if (sortBy === "newest") {
      return b.id - a.id;
    }

    if (sortBy === "oldest") {
      return a.id - b.id;
    }

    if (sortBy === "name") {
      return a.customer.localeCompare(b.customer);
    }

    if (sortBy === "status") {
      return a.status.localeCompare(b.status);
    }

    return 0;
  })
  .map((order) => (



            <tr key={order.id}>
              <td>#{order.id}</td>
              <td>{order.customer}</td>

              <td>
                <select
                  value={order.status}
                  onChange={(event) =>
                    updateStatus(order.id, event.target.value)
                  }
                >
                  <option value="Not Started">Not Started</option>
                  <option value="Printing">Printing</option>
                  <option value="Printed">Printed</option>
                  <option value="Shipped">Shipped</option>
                </select>
              </td>

              <td>
                <button
                  type="button"
                  className="delete-button"
                  onClick={() => deleteOrder(order.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
