const BASE = import.meta.env.VITE_API_BASE || "";

export async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${BASE}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(options.headers || {}),
      },
    });
  } catch {
    const error = new Error("后端没有连上");
    error.code = "NETWORK";
    throw error;
  }

  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { error: text };
    }
  }
  if (!response.ok) {
    const error = new Error(data?.error || "请求失败");
    error.code = data?.code || "HTTP";
    error.status = response.status;
    throw error;
  }
  return data;
}

export function getHealth() {
  return request("/api/health");
}

export function initDatabase() {
  return request("/api/admin/init", { method: "POST" });
}

export function importExcel() {
  return request("/api/admin/import-excel", { method: "POST" });
}

export function getSummary(year) {
  return request(`/api/summary?year=${year}`);
}

export function getFixedExpenses() {
  return request("/api/fixed-expenses");
}

export function createFixedExpense(body) {
  return request("/api/fixed-expenses", { method: "POST", body: JSON.stringify(body) });
}

export function updateFixedExpense(id, body) {
  return request(`/api/fixed-expenses/${id}`, { method: "PUT", body: JSON.stringify(body) });
}

export function deleteFixedExpense(id) {
  return request(`/api/fixed-expenses/${id}`, { method: "DELETE" });
}

export function getMonthly(year) {
  return request(`/api/monthly?year=${year}`);
}

export function saveMonthly(body) {
  return request("/api/monthly", { method: "PUT", body: JSON.stringify(body) });
}

export function createCategory(name) {
  return request("/api/monthly-categories", { method: "POST", body: JSON.stringify({ name }) });
}

export async function downloadCsv(path, filename) {
  let response;
  try {
    response = await fetch(`${BASE}${path}`);
  } catch {
    throw new Error("后端没有连上");
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || "导出失败");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
