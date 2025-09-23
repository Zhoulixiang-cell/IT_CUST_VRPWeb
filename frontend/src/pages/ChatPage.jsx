import { useState } from "react";
import ChatBox from "../components/ChatBox";
import { sendChat } from "../services/chat";

function ChatPage() {
  const [messages, setMessages] = useState([]);

  const handleSend = async (text) => {
    // 添加用户消息
    setMessages([...messages, { sender: "user", text }]);

    // 调用后端 API 获取 AI 回复
    const res = await sendChat("哈利波特", text);
    setMessages((prev) => [...prev, { sender: "ai", text: res.reply }]);
  };

  return (
    <div className="w-full max-w-2xl bg-white p-4 rounded shadow-md">
      <h1 className="text-xl font-bold mb-4">AI 角色扮演</h1>
      <ChatBox messages={messages} onSend={handleSend} />
    </div>
  );
}

export default ChatPage;