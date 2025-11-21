// Utilitário para gerar efeitos sonoros programaticamente

// Função para criar um som de sucesso (tom agudo e agradável)
export const playSuccessSound = () => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // Criar oscilador para o tom principal
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    // Conectar oscilador ao gain e ao destino
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // Configurar frequência (tom agudo e agradável)
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime); // Nota G5
    oscillator.frequency.setValueAtTime(1000, audioContext.currentTime + 0.1); // Nota C6
    
    // Configurar tipo de onda (sine para som suave)
    oscillator.type = 'sine';
    
    // Configurar envelope de volume (fade in/out)
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.05);
    gainNode.gain.linearRampToValueAtTime(0.2, audioContext.currentTime + 0.15);
    gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.3);
    
    // Tocar o som
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.3);
    
    console.log('[AUDIO] Som de sucesso reproduzido');
  } catch (error) {
    console.warn('[AUDIO] Erro ao reproduzir som de sucesso:', error);
  }
};

// Função para criar um som de erro (tom grave e distintivo)
export const playErrorSound = () => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // Criar oscilador para o tom principal
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    // Conectar oscilador ao gain e ao destino
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // Configurar frequência (tom grave e descendente)
    oscillator.frequency.setValueAtTime(400, audioContext.currentTime); // Nota G4
    oscillator.frequency.linearRampToValueAtTime(200, audioContext.currentTime + 0.2); // Desce para G3
    
    // Configurar tipo de onda (square para som mais áspero)
    oscillator.type = 'square';
    
    // Configurar envelope de volume
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.2, audioContext.currentTime + 0.05);
    gainNode.gain.linearRampToValueAtTime(0.15, audioContext.currentTime + 0.1);
    gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.4);
    
    // Tocar o som
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.4);
    
    console.log('[AUDIO] Som de erro reproduzido');
  } catch (error) {
    console.warn('[AUDIO] Erro ao reproduzir som de erro:', error);
  }
};

// Função para criar um som de escaneamento (bip rápido)
export const playScanSound = () => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // Criar oscilador para o bip
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    // Conectar oscilador ao gain e ao destino
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // Configurar frequência (tom médio)
    oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
    
    // Configurar tipo de onda
    oscillator.type = 'sine';
    
    // Configurar envelope de volume (bip curto)
    gainNode.gain.setValueAtTime(0, audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.25, audioContext.currentTime + 0.02);
    gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.1);
    
    // Tocar o som
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
    
    console.log('[AUDIO] Som de escaneamento reproduzido');
  } catch (error) {
    console.warn('[AUDIO] Erro ao reproduzir som de escaneamento:', error);
  }
};

// Função para verificar se o áudio está disponível
export const isAudioAvailable = () => {
  return !!(window.AudioContext || window.webkitAudioContext);
};

// Função para solicitar permissão de áudio (necessário em alguns navegadores)
export const requestAudioPermission = async () => {
  try {
    if (isAudioAvailable()) {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }
      return true;
    }
    return false;
  } catch (error) {
    console.warn('[AUDIO] Erro ao solicitar permissão de áudio:', error);
    return false;
  }
};