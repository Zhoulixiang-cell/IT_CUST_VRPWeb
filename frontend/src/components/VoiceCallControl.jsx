import React, { useState, useEffect } from 'react';

// 图标组件
const PhoneIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
  </svg>
);

const PhoneOffIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M17.34 14.54l-1.43-1.43c.69-.24 1.32-.57 1.88-1.01l2.2 2.2c.27.27.36.67.24 1.02-.37 1.12-.57 2.33-.57 3.57 0 .55-.45 1-1 1h-3.5c-.55 0-1-.45-1-1 0-1.25.2-2.45.57-3.57.11-.35.03-.74-.25-1.02l-2.2-2.2c.44-.56.77-1.19 1.01-1.88l1.43 1.43M2.27 1.72L1 3l9.97 9.97-2.2 2.2c-.27.27-.36.67-.24 1.02.37 1.12.57 2.33.57 3.57 0 .55.45 1 1 1H14c.14 0 .27-.04.38-.1L20 21l1.27-1.27L2.27 1.72z"/>
  </svg>
);

const VolumeUpIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
  </svg>
);

const MicIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2C13.1 2 14 2.9 14 4V12C14 13.1 13.1 14 12 14C10.9 14 10 13.1 10 12V4C10 2.9 10.9 2 12 2ZM19 11C19 15.4 15.4 19 11 19V21H13C13.6 21 14 21.4 14 22S13.6 23 13 23H11C10.4 23 10 22.6 10 22S10.4 21 11 21V19C6.6 19 3 15.4 3 11H5C5 14.3 7.7 17 11 17S17 14.3 17 11H19Z"/>
  </svg>
);

const VoiceCallControl = ({ 
  onStartCall, 
  onEndCall, 
  isInCall, 
  callStatus = 'idle', 
  voiceProvider = 'xunfei',
  currentRole = null 
}) => {
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(80);
  const [callDuration, setCallDuration] = useState(0);

  // 通话计时器
  useEffect(() => {
    let interval;
    if (isInCall && callStatus === 'connected') {
      interval = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    } else {
      setCallDuration(0);
    }
    return () => clearInterval(interval);
  }, [isInCall, callStatus]);

  // 格式化通话时长
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 获取状态文本和颜色
  const getStatusInfo = () => {
    switch (callStatus) {
      case 'connecting':
        return { text: '正在连接...', color: 'text-yellow-600' };
      case 'connected':
        return { text: `通话中 ${formatDuration(callDuration)}`, color: 'text-green-600' };
      case 'disconnected':
        return { text: '已断开连接', color: 'text-gray-600' };
      case 'error':
        return { text: '连接失败', color: 'text-red-600' };
      default:
        return { text: '准备就绪', color: 'text-blue-600' };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
      {/* 角色信息 */}
      {currentRole && (
        <div className="text-center mb-4">
          <div className="w-16 h-16 mx-auto mb-2 rounded-full overflow-hidden bg-gray-200">
            <img 
              src={currentRole.avatar_url} 
              alt={currentRole.name}
              className="w-full h-full object-cover"
            />
          </div>
          <h3 className="text-lg font-semibold text-gray-800">{currentRole.name}</h3>
          <p className="text-sm text-gray-600">{currentRole.description}</p>
        </div>
      )}

      {/* 语音服务提供商 */}
      <div className="text-center mb-4">
        <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
          voiceProvider === 'xunfei' 
            ? 'bg-blue-100 text-blue-700' 
            : 'bg-green-100 text-green-700'
        }`}>
          {voiceProvider === 'xunfei' ? '讯飞语音AI' : '百度语音'}
        </span>
      </div>

      {/* 通话状态 */}
      <div className="text-center mb-6">
        <div className={`text-sm font-medium ${statusInfo.color}`}>
          {statusInfo.text}
        </div>
        {callStatus === 'connecting' && (
          <div className="mt-2">
            <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
          </div>
        )}
      </div>

      {/* 通话控制按钮 */}
      <div className="flex justify-center items-center space-x-4 mb-6">
        {/* 主通话按钮 */}
        <button
          onClick={isInCall ? onEndCall : onStartCall}
          disabled={callStatus === 'connecting'}
          className={`p-4 rounded-full transition-all duration-200 ${
            isInCall
              ? 'bg-red-500 hover:bg-red-600'
              : 'bg-green-500 hover:bg-green-600'
          } text-white shadow-lg disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isInCall ? <PhoneOffIcon /> : <PhoneIcon />}
        </button>

        {/* 静音按钮 */}
        {isInCall && (
          <button
            onClick={() => setIsMuted(!isMuted)}
            className={`p-3 rounded-full transition-all duration-200 ${
              isMuted
                ? 'bg-red-100 text-red-600 hover:bg-red-200'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title={isMuted ? '取消静音' : '静音'}
          >
            <MicIcon />
          </button>
        )}

        {/* 音量控制 */}
        {isInCall && (
          <button
            className="p-3 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition-all duration-200"
            title="音量控制"
          >
            <VolumeUpIcon />
          </button>
        )}
      </div>

      {/* 音量控制滑块 */}
      {isInCall && (
        <div className="mb-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">音量</span>
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={(e) => setVolume(e.target.value)}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-sm text-gray-600 w-8">{volume}%</span>
          </div>
        </div>
      )}

      {/* 通话提示 */}
      <div className="text-center text-xs text-gray-500">
        {!isInCall ? (
          <p>点击通话按钮开始与AI角色进行语音对话</p>
        ) : (
          <p>您正在与 {currentRole?.name || 'AI角色'} 进行语音通话</p>
        )}
      </div>
    </div>
  );
};

export default VoiceCallControl;