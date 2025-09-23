import { useState, useEffect } from "react";
import ChatBox from "../components/ChatBox";
import { sendChatMessage, getRoles } from "../services/chat";

function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [loading, setLoading] = useState(true);

  // 加载角色列表
  useEffect(() => {
    const loadRoles = async () => {
      try {
        const roleList = await getRoles();
        setRoles(roleList);
        // 默认选择第一个角色
        if (roleList.length > 0) {
          setSelectedRole(roleList[0]);
        }
      } catch (error) {
        console.error("加载角色失败:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadRoles();
  }, []);

  const handleSend = async (text) => {
    if (!selectedRole) {
      alert("请先选择一个角色");
      return;
    }

    // 添加用户消息
    const userMessage = { sender: "user", text, timestamp: Date.now() };
    setMessages(prev => [...prev, userMessage]);

    try {
      // 调用后端 API 获取 AI 回复
      const response = await sendChatMessage(selectedRole.id, text);
      const aiMessage = { 
        sender: "ai", 
        text: response.reply, 
        timestamp: Date.now() 
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error("发送消息失败:", error);
      const errorMessage = { 
        sender: "ai", 
        text: "抱歉，消息发送失败，请稍后重试。", 
        timestamp: Date.now() 
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // 处理语音消息
  const handleVoiceMessage = async (audioBlob) => {
    if (!selectedRole) {
      alert("请先选择一个角色");
      return;
    }

    try {
      // 添加用户语音消息显示
      const userMessage = { 
        sender: "user", 
        text: "🎤 语音消息", 
        isVoice: true,
        audioBlob: audioBlob,
        timestamp: Date.now() 
      };
      setMessages(prev => [...prev, userMessage]);

      // TODO: 将来连接WebSocket发送语音数据
      // 暂时使用模拟回复
      setTimeout(() => {
        const aiMessage = { 
          sender: "ai", 
          text: `[${selectedRole.name}] 我收到了您的语音消息，但目前还在开发中。请使用文本输入。`, 
          timestamp: Date.now() 
        };
        setMessages(prev => [...prev, aiMessage]);
      }, 1000);
    } catch (error) {
      console.error("处理语音消息失败:", error);
      const errorMessage = { 
        sender: "ai", 
        text: "抱歉，语音消息处理失败。", 
        timestamp: Date.now() 
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleRoleChange = (role) => {
    setSelectedRole(role);
    // 清空对话历史并添加欢迎消息
    setMessages([{
      sender: "ai",
      text: `你好！我是${role.name}。${role.description}`,
      timestamp: Date.now()
    }]);
  };

  if (loading) {
    return (
      <div className="w-full max-w-2xl bg-white p-4 rounded shadow-md">
        <div className="text-center">加载中...</div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl bg-white rounded-lg shadow-lg overflow-hidden">
      {/* 头部 - 角色选择 */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4">
        <h1 className="text-2xl font-bold mb-3">AI 角色扮演聊天</h1>
        <div className="flex flex-wrap gap-2">
          {roles.map((role) => (
            <button
              key={role.id}
              onClick={() => handleRoleChange(role)}
              className={`px-4 py-2 rounded-full transition-colors ${
                selectedRole?.id === role.id
                  ? 'bg-white text-blue-600 font-medium'
                  : 'bg-blue-400 hover:bg-blue-300 text-white'
              }`}
            >
              {role.name}
            </button>
          ))}
        </div>
        {selectedRole && (
          <p className="mt-2 text-blue-100 text-sm">{selectedRole.description}</p>
        )}
      </div>

      {/* 聊天区域 */}
      <div className="p-4">
        <ChatBox 
          messages={messages} 
          onSend={handleSend}
          onVoiceMessage={handleVoiceMessage}
          selectedRole={selectedRole}
        />
      </div>
    </div>
  );
}

export default ChatPage;