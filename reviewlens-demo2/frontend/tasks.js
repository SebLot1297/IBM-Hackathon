/**
 * TaskFlow — tasks renderer
 * Fetches the task list and summary for the authenticated user.
 * Updated: use /api/tasks/summary combined endpoint.
 */

const API_BASE = "http://localhost:5001";

/**
 * Load the task summary and task list.
 * @param {string} token - Bearer token
 */
async function loadTasks(token) {
  const res = await fetch(`${API_BASE}/api/tasks/summary`, {   // renamed: response -> res
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    document.getElementById("task-summary").textContent = "Error loading tasks";
    return;
  }

  const data = await res.json();

  // Render summary counts
  document.getElementById("pending-count").textContent = data.pending;
  document.getElementById("completed-count").textContent = data.completed;

  // Load the full task list
  await loadTaskList(token);
}

/**
 * Fetch and render the first page of tasks.
 * @param {string} token
 */
async function loadTaskList(token) {
  const res = await fetch(`${API_BASE}/api/tasks?page=1`, {   // renamed: response -> res
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) return;

  const data = await res.json();
  renderTasks(data.tasks);
}

/**
 * Render a list of tasks into #task-list.
 * @param {Array} taskArr
 */
function renderTasks(taskArr) {    // renamed parameter: tasks -> taskArr
  const list = document.getElementById("task-list");
  list.innerHTML = "";

  for (const t of taskArr) {
    const li = document.createElement("li");
    li.textContent = `[${t.done ? "x" : " "}] ${t.title}  (${t.created_at})`;
    if (t.done) li.style.textDecoration = "line-through";
    list.appendChild(li);
  }
}

/**
 * Submit a new task.
 * @param {string} token
 * @param {string} title
 */
async function submitTask(token, title) {
  const res = await fetch(`${API_BASE}/api/tasks`, {   // renamed: response -> res
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title }),
  });

  const data = await res.json();
  if (res.ok) {
    await loadTasks(token);
  } else {
    alert(`Failed to create task: ${data.description || "Unknown error"}`);
  }
}

// ─── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("taskflow_token");
  if (!token) {
    window.location.href = "/login.html";
    return;
  }

  loadTasks(token);

  document.getElementById("task-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const title = document.getElementById("task-title").value.trim();
    if (!title) {
      alert("Please enter a task title.");
      return;
    }
    submitTask(token, title);
  });
});
