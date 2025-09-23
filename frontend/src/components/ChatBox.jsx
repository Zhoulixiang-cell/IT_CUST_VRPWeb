import { useState } from "react";

function ChatBox({ messages, onSend }) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput("");
    }
  };

  return (
    <div>
      <div className="h-64 overflow-y-auto border p-2 mb-2">
        {messages.map((m, i) => (
          <div key={i} className={m.sender === "user" ? "text-right" : "text-left"}>
            <span
              className={`inline-block p-2 my-1 rounded ${
                m.sender === "user" ? "bg-blue-200" : "bg-green-200"
              }`}
            >
              {m.text}
            </span>
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          className="flex-1 border p-2 rounded-l"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入消息..."
        />
        <button className="bg-blue-500 text-white px-4 rounded-r" onClick={handleSend}>
          发送
        </button>
      </div>
    </div>
  );
}

export default ChatBox;