const API_BASE_URL = "http://localhost:8000";

// 获取角色列表
export async function getRoles() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/roles/`);
    if (!response.ok) {
      throw new Error('获取角色列表失败');
    }
    return await response.json();
  } catch (error) {
    console.error("获取角色列表错误:", error);
    throw error;
  }
}

// 发送聊天消息（HTTP版本）
export async function sendChatMessage(roleId, message) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/text`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ 
        role_id: roleId, 
        message: message 
      }),
    });
    
    if (!response.ok) {
      throw new Error('发送消息失败');
    }
    
    return await response.json();
  } catch (error) {
    console.error("发送消息错误:", error);
    throw error;
  }
}

// WebSocket连接类（用于实时聊天）
export class ChatWebSocket {
  constructor(sessionId, roleId) {
    this.sessionId = sessionId;
    this.roleId = roleId;
    this.ws = null;
    this.onMessage = null;
    this.onError = null;
    this.onClose = null;
  }

  connect() {
    const wsUrl = `ws://localhost:8000/ws/api/session/${this.sessionId}/${this.roleId}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket连接已建立');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (this.onMessage) {
          this.onMessage(data);
        }
      } catch (error) {
        console.error('解析WebSocket消息失败:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
      if (this.onError) {
        this.onError(error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket连接已关闭');
      if (this.onClose) {
        this.onClose(event);
      }
    };
  }

  sendMessage(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ text: message }));
    } else {
      console.error('WebSocket未连接');
    }
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}