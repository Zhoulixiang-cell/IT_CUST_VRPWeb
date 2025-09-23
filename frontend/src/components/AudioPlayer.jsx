import React, { useState, useEffect } from 'react';

// 原生SVG图标替代 lucide-react
const PlayIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
    <path d="M8 5v14l11-7z"/>
  </svg>
);

const PauseIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
  </svg>
);

const VolumeXIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
    <path d="M16.5 12C16.5 10.23 15.48 8.71 14 7.97V10.18L16.45 12.63C16.5 12.43 16.5 12.21 16.5 12ZM19 12C19 12.94 18.8 13.82 18.46 14.64L19.97 16.15C20.62 14.91 21 13.5 21 12C21 7.72 18 4.14 14 3.23V5.29C16.89 6.15 19 8.83 19 12ZM4.27 3L3 4.27L7.73 9H3V15H7L12 20V13.27L16.25 17.52C15.58 18.04 14.83 18.45 14 18.7V20.76C15.38 20.45 16.63 19.81 17.68 18.96L19.73 21L21 19.73L12 10.73L4.27 3ZM12 4L9.91 6.09L12 8.18V4Z"/>
  </svg>
);

import webSpeechService from '../services/webSpeech';

const AudioPlayer = ({ text, roleId, autoPlay = false, onPlayStart, onPlayEnd }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSupported, setIsSupported] = useState(true);

  useEffect(() => {
    setIsSupported(webSpeechService.isSupported);
  }, []);

  useEffect(() => {
    if (autoPlay && text && !isPlaying) {
      handlePlay();
    }
  }, [text, autoPlay]);

  const handlePlay = async () => {
    if (!text || !isSupported) return;

    try {
      setIsPlaying(true);
      if (onPlayStart) onPlayStart();

      await webSpeechService.speak(text, roleId, {
        rate: 0.9,
        pitch: 1.0,
        volume: 0.8
      });

      setIsPlaying(false);
      if (onPlayEnd) onPlayEnd();
    } catch (error) {
      console.error('语音播放失败:', error);
      setIsPlaying(false);
      if (onPlayEnd) onPlayEnd();
    }
  };

  const handleStop = () => {
    webSpeechService.stop();
    setIsPlaying(false);
    if (onPlayEnd) onPlayEnd();
  };

  if (!isSupported) {
    return (
      <div className="text-xs text-gray-400 flex items-center">
        <VolumeXIcon />
        <span className="ml-1">浏览器不支持语音播放</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-1 mt-2">
      <button
        onClick={isPlaying ? handleStop : handlePlay}
        disabled={!text}
        className={`p-1 rounded-full transition-all duration-200 ${
          isPlaying
            ? 'bg-orange-500 hover:bg-orange-600 text-white'
            : 'bg-blue-500 hover:bg-blue-600 text-white disabled:bg-gray-300'
        }`}
        title={isPlaying ? '停止播放' : '播放语音'}
      >
        {isPlaying ? <PauseIcon /> : <PlayIcon />}
      </button>
      
      <span className="text-xs text-gray-500">
        {isPlaying ? '正在播放...' : '点击播放'}
      </span>
      
      {isPlaying && (
        <div className="flex space-x-1">
          <div className="w-1 h-3 bg-blue-500 animate-pulse"></div>
          <div className="w-1 h-2 bg-blue-400 animate-pulse" style={{animationDelay: '0.1s'}}></div>
          <div className="w-1 h-4 bg-blue-600 animate-pulse" style={{animationDelay: '0.2s'}}></div>
        </div>
      )}
    </div>
  );
};

export default AudioPlayer;