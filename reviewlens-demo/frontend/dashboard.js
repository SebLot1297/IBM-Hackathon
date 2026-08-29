/**
 * FinPay — dashboard renderer
 * Fetches balance and recent transactions for the authenticated user.
 * Updated: use /api/dashboard combined endpoint.
 */

const API_BASE = "http://localhost:5000";

/**
 * Load full dashboard data from the new combined endpoint.
 * @param {string} token - Bearer token
 */
async function loadDashboard(token) {
  const res = await fetch(`${API_BASE}/api/dashboard`, {   // renamed: response -> res
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    document.getElementById("balance-display").textContent = "Error loading dashboard";
    return;
  }

  const data = await res.json();

  // Render balance
  document.getElementById("balance-display").textContent =
    `$${data.balance.toFixed(2)}`;

  // Render summary
  document.getElementById("total-sent").textContent =
    `$${data.summary.total_sent.toFixed(2)}`;
  document.getElementById("total-received").textContent =
    `$${data.summary.total_received.toFixed(2)}`;

  // Render transactions
  renderTransactions(data.recent_transactions);
}

/**
 * Render a list of transactions into #tx-list.
 * @param {Array} txList
 */
function renderTransactions(txList) {  // renamed parameter: transactions -> txList
  const list = document.getElementById("tx-list");
  list.innerHTML = "";

  for (const tx of txList) {
    const li = document.createElement("li");
    li.textContent = `${tx.ts}  |  ${tx.from} → ${tx.to}  |  $${tx.amount.toFixed(2)}`;
    list.appendChild(li);
  }
}

/**
 * Submit a transfer form.
 * @param {string} token
 * @param {string} recipientId
 * @param {number} amount
 */
async function submitTransfer(token, recipientId, amount) {
  const res = await fetch(`${API_BASE}/api/transfer`, {   // renamed: response -> res
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ recipient_id: recipientId, amount }),
  });

  const data = await res.json();
  if (res.ok) {
    alert(`Transfer successful! ID: ${data.transaction_id}`);
    await loadDashboard(token);
  } else {
    alert(`Transfer failed: ${data.description || "Unknown error"}`);
  }
}

// ─── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("finpay_token");
  if (!token) {
    window.location.href = "/login.html";
    return;
  }

  loadDashboard(token);

  document.getElementById("transfer-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const recipient = document.getElementById("recipient-id").value.trim();
    const amount = parseFloat(document.getElementById("amount").value);
    if (!recipient || isNaN(amount) || amount <= 0) {
      alert("Please enter a valid recipient and amount.");
      return;
    }
    submitTransfer(token, recipient, amount);
  });
});
