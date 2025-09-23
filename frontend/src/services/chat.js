export async function sendChat(role, message) {
  const res = await fetch("http://localhost:8000/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role, message }),
  });
  return res.json();
}