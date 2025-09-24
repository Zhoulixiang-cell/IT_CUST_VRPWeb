import React, { useState, useRef, useEffect } from 'react';

// 原生SVG图标替代 lucide-react
const MicIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2C13.1 2 14 2.9 14 4V12C14 13.1 13.1 14 12 14C10.9 14 10 13.1 10 12V4C10 2.9 10.9 2 12 2ZM19 11C19 15.4 15.4 19 11 19V21H13C13.6 21 14 21.4 14 22S13.6 23 13 23H11C10.4 23 10 22.6 10 22S10.4 21 11 21V19C6.6 19 3 15.4 3 11H5C5 14.3 7.7 17 11 17S17 14.3 17 11H19Z"/>
  </svg>
);

const MicOffIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M19 11C19 12.19 18.66 13.3 18.1 14.28L16.87 13.05C17.14 12.43 17.3 11.74 17.3 11H19ZM15.18 10.2L9.85 4.87C10.18 4.73 10.54 4.65 10.92 4.65C12.66 4.65 14.08 6.07 14.08 7.81V10.2H15.18ZM4.27 3L21 19.73L19.73 21L15.54 16.81C14.77 17.27 13.91 17.58 13 17.72V21H17V23H7V21H11V17.72C7.72 17.23 5 14.41 5 11H7C7 13.76 9.24 16 12 16C12.81 16 13.6 15.79 14.31 15.45L4.27 3Z"/>
  </svg>
);

const VolumeIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M3 9V15H7L12 20V4L7 9H3ZM16.5 12C16.5 10.23 15.48 8.71 14 7.97V16.02C15.48 15.29 16.5 13.77 16.5 12Z"/>
  </svg>
);

const VolumeXIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M16.5 12C16.5 10.23 15.48 8.71 14 7.97V10.18L16.45 12.63C16.5 12.43 16.5 12.21 16.5 12ZM19 12C19 12.94 18.8 13.82 18.46 14.64L19.97 16.15C20.62 14.91 21 13.5 21 12C21 7.72 18 4.14 14 3.23V5.29C16.89 6.15 19 8.83 19 12ZM4.27 3L3 4.27L7.73 9H3V15H7L12 20V13.27L16.25 17.52C15.58 18.04 14.83 18.45 14 18.7V20.76C15.38 20.45 16.63 19.81 17.68 18.96L19.73 21L21 19.73L12 10.73L4.27 3ZM12 4L9.91 6.09L12 8.18V4Z"/>
  </svg>
);

const VoiceRecorder = ({ onVoiceMessage, isRecording, setIsRecording, voiceProvider = 'xunfei' }) => {
  const [hasPermission, setHasPermission] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState('idle'); // idle, recording, processing, error
  const [statusMessage, setStatusMessage] = useState('');
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const audioRef = useRef(null);

  // 请求麦克风权限
  useEffect(() => {
    const requestPermission = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        setHasPermission(true);
        stream.getTracks().forEach(track => track.stop()); // 立即停止以释放资源
      } catch (error) {
        console.error('麦克风权限被拒绝:', error);
        setHasPermission(false);
      }
    };
    requestPermission();
  }, []);

  // 开始录音
  const startRecording = async () => {
    if (!hasPermission) {
      alert('请授权麦克风权限');
      return;
    }

    try {
      setVoiceStatus('recording');
      setStatusMessage('正在录音...');
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      });

      streamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      const chunks = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        setVoiceStatus('processing');
        setStatusMessage(`正在使用${voiceProvider === 'xunfei' ? '讯飞' : '百度'}语音识别...`);
        
        const blob = new Blob(chunks, { type: 'audio/webm;codecs=opus' });
        setAudioBlob(blob);
        
        // 停止所有音轨
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        
        // 自动发送录音
        if (onVoiceMessage) {
          onVoiceMessage(blob);
        }
        
        // 重置状态
        setTimeout(() => {
          setVoiceStatus('idle');
          setStatusMessage('');
        }, 2000);
      };

      mediaRecorder.onerror = (event) => {
        setVoiceStatus('error');
        setStatusMessage('录音出现错误');
        console.error('录音错误:', event);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('开始录音失败:', error);
      setVoiceStatus('error');
      setStatusMessage('录音失败，请检查麦克风权限');
      alert('录音失败，请检查麦克风权限');
    }
  };

  // 停止录音
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setVoiceStatus('processing');
      setStatusMessage('正在处理音频...');
    }
  };

  // 播放录音
  const playRecording = () => {
    if (audioBlob && audioRef.current) {
      const audioUrl = URL.createObjectURL(audioBlob);
      audioRef.current.src = audioUrl;
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  // 停止播放
  const stopPlaying = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-2">
      {/* 语音服务提供商显示 */}
      <div className="text-xs text-gray-500 flex items-center space-x-1">
        <span>语音服务:</span>
        <span className={`px-2 py-1 rounded-full text-xs ${
          voiceProvider === 'xunfei' 
            ? 'bg-blue-100 text-blue-600' 
            : 'bg-green-100 text-green-600'
        }`}>
          {voiceProvider === 'xunfei' ? '讯飞语音' : '百度语音'}
        </span>
      </div>
      
      <div className="flex items-center space-x-2">
        {/* 录音按钮 */}
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!hasPermission || voiceStatus === 'processing'}
          className={`p-3 rounded-full transition-all duration-200 ${
            voiceStatus === 'processing'
              ? 'bg-yellow-500 animate-pulse cursor-not-allowed'
              : isRecording
              ? 'bg-red-500 hover:bg-red-600 animate-pulse'
              : hasPermission
              ? 'bg-blue-500 hover:bg-blue-600'
              : 'bg-gray-400 cursor-not-allowed'
          } text-white shadow-lg`}
          title={
            voiceStatus === 'processing' 
              ? '正在处理...' 
              : isRecording 
              ? '停止录音' 
              : '开始录音'
          }
        >
          {voiceStatus === 'processing' ? (
            <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
          ) : isRecording ? (
            <MicOffIcon />
          ) : (
            <MicIcon />
          )}
        </button>

        {/* 播放录音按钮 */}
        {audioBlob && (
          <button
            onClick={isPlaying ? stopPlaying : playRecording}
            className={`p-2 rounded-full transition-all duration-200 ${
              isPlaying
                ? 'bg-orange-500 hover:bg-orange-600'
                : 'bg-green-500 hover:bg-green-600'
            } text-white shadow-lg`}
            title={isPlaying ? '停止播放' : '播放录音'}
          >
            {isPlaying ? <VolumeXIcon /> : <VolumeIcon />}
          </button>
        )}
      </div>

      {/* 状态显示 */}
      {statusMessage && (
        <div className={`text-sm font-medium ${
          voiceStatus === 'recording' 
            ? 'text-red-500 animate-pulse' 
            : voiceStatus === 'processing'
            ? 'text-yellow-600'
            : voiceStatus === 'error'
            ? 'text-red-600'
            : 'text-green-500'
        }`}>
          {statusMessage}
        </div>
      )}

      {/* 权限状态提示 */}
      {!hasPermission && (
        <span className="text-gray-500 text-sm">
          请授权麦克风权限
        </span>
      )}

      {/* 隐藏的音频元素 */}
      <audio
        ref={audioRef}
        onEnded={() => setIsPlaying(false)}
        style={{ display: 'none' }}
      />
    </div>
  );
};

export default VoiceRecorder;