
import { useEffect, useState } from "react";
import Login from "./Login";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  // Authentication
  const [token, setToken] = useState(null);

  // Order state
  const [orders, setOrders] = useState([]);
  const [newOrderId, setNewOrderId] = useState("");
  const [newCustomer, setNewCustomer] = useState("");
  const [loadingOrders, setLoadingOrders] = useState(false);

  // Filters
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [sortBy, setSortBy] = useState("newest");

  // Authentication helpers
  function handleSessionExpired() {
    setToken(null);
    setOrders([]);
    alert("Your session has expired or is invalid. Please log in again.");
  }

  function handleLogout() {
    setToken(null);
    setOrders([]);
    setNewOrderId("");
    setNewCustomer("");
    setSearchTerm("");
    setStatusFilter("All");
    setSortBy("newest");
  }

  // Load orders after login
  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;

    async function loadOrders() {
      setLoadingOrders(true);

      try {
        const response = await fetch(`${API_URL}/orders`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (cancelled) return;

        if (response.status === 401) {
          handleSessionExpired();
          return;
        }

        if (!response.ok) {
          throw new Error("Failed to load orders");
        }

        const data = await response.json();

        if (!cancelled) {
          setOrders(data);
        }
      } catch (error) {
        if (!cancelled) {
          console.error(error);
          alert("Failed to load orders. Please try again.");
        }
      } finally {
        if (!cancelled) {
          setLoadingOrders(false);
        }
      }
    }

    loadOrders();

    return () => {
      cancelled = true;
    };
  }, [token]);

  // Add a new order
  async function addOrder(event) {
    event.preventDefault();

    const newOrder = {
      id: Number(newOrderId),
      customer: newCustomer.trim(),
      status: "Not Started",
    };

    if (
      !Number.isSafeInteger(newOrder.id) ||
      newOrder.id <= 0 ||
      !newOrder.customer
    ) {
      alert("Please enter a valid Order ID and customer name.");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/orders`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(newOrder),
      });

      if (response.status === 401) {
        handleSessionExpired();
        return;
      }

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error("This Order ID already exists.");
        }

        throw new Error("Failed to add order.");
      }

      // Refresh orders from the database
      const ordersResponse = await fetch(`${API_URL}/orders`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (ordersResponse.status === 401) {
        handleSessionExpired();
        return;
      }

      if (!ordersResponse.ok) {
        throw new Error(
          "Order saved, but failed to refresh the dashboard."
        );
      }

      const updatedOrders = await ordersResponse.json();

      setOrders(updatedOrders);
      setNewOrderId("");
      setNewCustomer("");
    } catch (error) {
      console.error(error);
      alert(error.message);
    }
  }

  // Update order status
  async function updateStatus(orderId, newStatus) {
    try {
      const response = await fetch(
        `${API_URL}/orders/${orderId}/status`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (response.status === 401) {
        handleSessionExpired();
        return;
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || "Failed to update order."
        );
      }

      const data = await response.json();

      setOrders((previousOrders) =>
        previousOrders.map((order) =>
          order.id === orderId
            ? { ...order, status: data.order.status }
            : order
        )
      );
    } catch (error) {
      console.error(error);
      alert(error.message);
    }
  }

  // Delete an order
  async function deleteOrder(orderId) {
    const confirmed = window.confirm(
      `Are you sure you want to delete order #${orderId}?`
    );

    if (!confirmed) return;

    try {
      const response = await fetch(
        `${API_URL}/orders/${orderId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 401) {
        handleSessionExpired();
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to delete order.");
      }

      setOrders((previousOrders) =>
        previousOrders.filter(
          (order) => order.id !== orderId
        )
      );
    } catch (error) {
      console.error(error);
      alert(error.message);
    }
  }

  // Dashboard statistics
  const totalOrders = orders.length;

  const notStartedCount = orders.filter(
    (order) => order.status === "Not Started"
  ).length;

  const printingCount = orders.filter(
    (order) => order.status === "Printing"
  ).length;

  const printedCount = orders.filter(
    (order) => order.status === "Printed"
  ).length;

  const shippedCount = orders.filter(
    (order) => order.status === "Shipped"
  ).length;

  // Search, filter and sort
  const filteredOrders = orders
    .filter((order) => {
      const matchesSearch =
        order.customer
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        String(order.id).includes(searchTerm);

      const matchesStatus =
        statusFilter === "All" ||
        order.status === statusFilter;

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
    });

  // Login screen
  if (!token) {
    return <Login onLogin={setToken} />;
  }

  return (
    <div className="flow-dashboard">

      {/* HEADER */}
      <header className="flow-header">
        <div className="flow-brand">
          <div className="flow-logo" aria-hidden="true">
            ↗
          </div>
          <span>flow.</span>
        </div>

        <nav
          className="flow-navigation"
          aria-label="Main navigation"
        >
          <span className="nav-active">
            Overview
          </span>

          <span className="nav-coming-soon">
            Analytics · Coming soon
          </span>
        </nav>

        <button
          type="button"
          className="logout-button"
          onClick={handleLogout}
        >
          Log out
        </button>
      </header>

      {/* WELCOME */}
      <section className="flow-welcome">
        <h1>Business overview</h1>
        <p>
          Track your orders and business activity in one place.
        </p>
      </section>

      {/* SUMMARY CARDS */}
      <section
        className="summary-container"
        aria-label="Order statistics"
      >
        <div className="summary-card">
          <h3>Total Orders</h3>
          <p>{totalOrders}</p>
        </div>

        <div className="summary-card">
          <h3>Not Started</h3>
          <p>{notStartedCount}</p>
        </div>

        <div className="summary-card">
          <h3>Printing</h3>
          <p>{printingCount}</p>
        </div>

        <div className="summary-card">
          <h3>Printed</h3>
          <p>{printedCount}</p>
        </div>

        <div className="summary-card">
          <h3>Shipped</h3>
          <p>{shippedCount}</p>
        </div>
      </section>

      {/* ADD ORDER FORM */}
      <section className="order-form">
        <h2>Add New Order</h2>

        <form onSubmit={addOrder}>
          <input
            type="number"
            min="1"
            step="1"
            placeholder="Order ID"
            aria-label="Order ID"
            value={newOrderId}
            onChange={(event) =>
              setNewOrderId(event.target.value)
            }
            required
          />

          <input
            type="text"
            placeholder="Customer Name"
            aria-label="Customer Name"
            value={newCustomer}
            onChange={(event) =>
              setNewCustomer(event.target.value)
            }
            required
          />

          <input
            type="text"
            value="Not Started"
            aria-label="Initial order status"
            disabled
            title="New orders always start as Not Started"
          />

          <button type="submit">
            Add Order
          </button>
        </form>
      </section>

      {/* CUSTOMER ORDERS */}
      <section className="orders-section">
        <div className="orders-heading">
          <h2>Customer Orders</h2>
          <span className="order-count">
            {totalOrders} total
          </span>
        </div>

        {/* SEARCH AND FILTERS */}
        <div className="order-filters">
          <input
            type="text"
            placeholder="Search customer or order ID..."
            aria-label="Search orders"
            value={searchTerm}
            onChange={(event) =>
              setSearchTerm(event.target.value)
            }
          />

          <select
            aria-label="Filter by status"
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value)
            }
          >
            <option value="All">All Statuses</option>
            <option value="Not Started">Not Started</option>
            <option value="Printing">Printing</option>
            <option value="Printed">Printed</option>
            <option value="Shipped">Shipped</option>
          </select>

          <select
            aria-label="Sort orders"
            value={sortBy}
            onChange={(event) =>
              setSortBy(event.target.value)
            }
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="name">Customer A-Z</option>
            <option value="status">Status A-Z</option>
          </select>
        </div>

        {/* ORDERS TABLE */}
        <div className="table-container">
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
              {loadingOrders ? (
                <tr>
                  <td colSpan={4} className="empty-state">
                    Loading orders...
                  </td>
                </tr>
              ) : filteredOrders.length === 0 ? (
                <tr>
                  <td colSpan={4} className="empty-state">
                    <div className="empty-state-content">
                      <div
                        className="empty-state-icon"
                        aria-hidden="true"
                      >
                        ◎
                      </div>

                      <h3>
                        {orders.length === 0
                          ? "No orders yet"
                          : "No matching orders"}
                      </h3>

                      <p>
                        {orders.length === 0
                          ? "Create your first order above to get started."
                          : "Try changing your search or filters."}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredOrders.map((order) => (
                  <tr key={order.id}>
                    <td className="order-id">
                      #{order.id}
                    </td>

                    <td>{order.customer}</td>

                    <td>
                      <select
                        aria-label={`Status for order ${order.id}`}
                        value={order.status}
                        onChange={(event) =>
                          updateStatus(
                            order.id,
                            event.target.value
                          )
                        }
                        disabled={order.status === "Shipped"}
                      >
                        <option value={order.status}>
                          {order.status}
                        </option>

                        {order.status === "Not Started" && (
                          <option value="Printing">
                            Printing
                          </option>
                        )}

                        {order.status === "Printing" && (
                          <option value="Printed">
                            Printed
                          </option>
                        )}

                        {order.status === "Printed" && (
                          <option value="Shipped">
                            Shipped
                          </option>
                        )}
                      </select>
                    </td>

                    <td>
                      <button
                        type="button"
                        className="delete-button"
                        onClick={() =>
                          deleteOrder(order.id)
                        }
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default App;
