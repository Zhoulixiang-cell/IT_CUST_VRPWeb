import { useState, useRef, useEffect } from "react";
import VoiceRecorder from "./VoiceRecorder";
import AudioPlayer from "./AudioPlayer";

function ChatBox({ messages, onSend, onVoiceMessage, selectedRole }) {
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-96">
      {/* 消息显示区域 */}
      <div className="flex-1 overflow-y-auto border rounded-lg p-4 mb-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            {selectedRole ? `开始与${selectedRole.name}对话吧！` : '请选择一个角色开始对话'}
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === "user"
                    ? "bg-blue-500 text-white rounded-br-none"
                    : "bg-white border border-gray-200 text-gray-800 rounded-bl-none shadow-sm"
                }`}
              >
                <div className="text-sm">{message.text}</div>
                {message.timestamp && (
                  <div className={`text-xs mt-1 ${
                    message.sender === "user" ? "text-blue-100" : "text-gray-400"
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                )}
                
                {/* AI消息附加语音播放按钮 */}
                {message.sender === "ai" && (
                  <AudioPlayer 
                    text={message.text}
                    roleId={selectedRole?.id}
                    autoPlay={false}
                  />
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={selectedRole ? `与${selectedRole.name}对话...` : "请先选择角色"}
          disabled={!selectedRole || isRecording}
        />
        
        {/* 语音录制组件 */}
        <VoiceRecorder
          onVoiceMessage={onVoiceMessage}
          isRecording={isRecording}
          setIsRecording={setIsRecording}
        />
        
        <button
          onClick={handleSend}
          disabled={!selectedRole || !input.trim() || isRecording}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          发送
        </button>
      </div>
    </div>
  );
}

export default ChatBox;