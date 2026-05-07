type JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };

type JsonRecord = { [key: string]: JsonValue };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function postJson(path: string, body: JsonRecord) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}
