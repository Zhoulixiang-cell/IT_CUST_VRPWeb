/**
 * 浏览器Web Speech API服务
 * 提供免费的语音合成功能
 */

class WebSpeechService {
  constructor() {
    this.synth = window.speechSynthesis;
    this.voices = [];
    this.currentVoice = null;
    this.isSupported = 'speechSynthesis' in window;
    
    if (this.isSupported) {
      this.loadVoices();
      // 监听语音列表变化
      if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = () => this.loadVoices();
      }
    }
  }

  loadVoices() {
    this.voices = this.synth.getVoices();
    
    // 根据角色选择合适的语音
    this.setupRoleVoices();
  }

  setupRoleVoices() {
    this.roleVoices = {
      'socrates': this.findVoice(['zh-CN', 'zh'], 'male') || this.findVoice(['en-US', 'en'], 'male'),
      'harry': this.findVoice(['en-GB', 'en-US', 'en'], 'male') || this.findVoice(['zh-CN', 'zh'], 'male'),
      'holmes': this.findVoice(['en-GB', 'en-US', 'en'], 'male') || this.findVoice(['zh-CN', 'zh'], 'male')
    };
  }

  findVoice(languages, gender = null) {
    for (const lang of languages) {
      let voice = this.voices.find(v => 
        v.lang.startsWith(lang) && 
        (!gender || v.name.toLowerCase().includes(gender))
      );
      if (voice) return voice;
      
      // 如果没找到指定性别，返回该语言的第一个语音
      voice = this.voices.find(v => v.lang.startsWith(lang));
      if (voice) return voice;
    }
    return this.voices[0]; // 返回默认语音
  }

  speak(text, roleId = null, options = {}) {
    if (!this.isSupported) {
      console.warn('浏览器不支持语音合成');
      return Promise.reject('浏览器不支持语音合成');
    }

    return new Promise((resolve, reject) => {
      // 停止当前播放
      this.synth.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      
      // 选择语音
      if (roleId && this.roleVoices[roleId]) {
        utterance.voice = this.roleVoices[roleId];
      } else if (this.currentVoice) {
        utterance.voice = this.currentVoice;
      }

      // 设置参数
      utterance.rate = options.rate || 0.9;     // 语速
      utterance.pitch = options.pitch || 1.0;   // 音调
      utterance.volume = options.volume || 0.8; // 音量

      // 根据角色调整语音特性
      if (roleId) {
        switch (roleId) {
          case 'socrates':
            utterance.rate = 0.8;   // 苏格拉底说话较慢
            utterance.pitch = 0.9;  // 稍低音调
            break;
          case 'harry':
            utterance.rate = 1.0;   // 哈利说话正常
            utterance.pitch = 1.1;  // 稍高音调，年轻
            break;
          case 'holmes':
            utterance.rate = 1.1;   // 福尔摩斯说话较快
            utterance.pitch = 0.95; // 略低音调，理性
            break;
        }
      }

      // 事件监听
      utterance.onstart = () => {
        console.log('开始语音播放');
      };

      utterance.onend = () => {
        console.log('语音播放结束');
        resolve();
      };

      utterance.onerror = (event) => {
        console.error('语音播放错误:', event);
        reject(event.error);
      };

      utterance.onpause = () => {
        console.log('语音播放暂停');
      };

      utterance.onresume = () => {
        console.log('语音播放恢复');
      };

      // 开始播放
      this.synth.speak(utterance);
    });
  }

  stop() {
    if (this.isSupported) {
      this.synth.cancel();
    }
  }

  pause() {
    if (this.isSupported && this.synth.speaking) {
      this.synth.pause();
    }
  }

  resume() {
    if (this.isSupported && this.synth.paused) {
      this.synth.resume();
    }
  }

  isPlaying() {
    return this.isSupported && this.synth.speaking;
  }

  isPaused() {
    return this.isSupported && this.synth.paused;
  }

  getAvailableVoices() {
    return this.voices.map(voice => ({
      name: voice.name,
      lang: voice.lang,
      gender: voice.name.toLowerCase().includes('female') ? 'female' : 'male'
    }));
  }

  setVoice(voiceName) {
    const voice = this.voices.find(v => v.name === voiceName);
    if (voice) {
      this.currentVoice = voice;
      return true;
    }
    return false;
  }
}

// 创建全局实例
const webSpeechService = new WebSpeechService();

export default webSpeechService;