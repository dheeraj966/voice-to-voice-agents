'use client';

import { useEffect, useState } from 'react';
import {
  API,
  backendConfig,
  resetBackendConfig,
  setBackendUrl,
  setLivekitUrl,
} from '@/lib/backend-config';

interface BackendStatus {
  connected: boolean;
  status: 'checking' | 'connected' | 'disconnected' | 'error';
  message?: string;
  ollamaAvailable?: boolean;
  model?: string;
}

export function useBackendConnection() {
  const [status, setStatus] = useState<BackendStatus>({
    connected: false,
    status: 'checking',
  });

  const checkConnection = async () => {
    setStatus((prev) => ({ ...prev, status: 'checking' }));

    try {
      const response = await fetch(API.health(), {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        // Important: allow CORS
        mode: 'cors',
      });

      if (response.ok) {
        const data = await response.json();
        setStatus({
          connected: true,
          status: 'connected',
          message: `Connected to ${backendConfig.apiUrl}`,
          ollamaAvailable: data.ollama_available,
          model: data.model,
        });
      } else {
        setStatus({
          connected: false,
          status: 'error',
          message: `Backend returned ${response.status}`,
        });
      }
    } catch (error) {
      setStatus({
        connected: false,
        status: 'disconnected',
        message: `Cannot reach backend at ${backendConfig.apiUrl}`,
      });
    }
  };

  useEffect(() => {
    checkConnection();
    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  return {
    ...status,
    backendUrl: backendConfig.apiUrl,
    livekitUrl: backendConfig.livekitUrl,
    checkConnection,
    setBackendUrl,
    setLivekitUrl,
    resetBackendConfig,
  };
}

// Hook for making API calls to the backend
export function useBackendAPI() {
  const sendMessage = async (
    message: string,
    options?: {
      sessionId?: string;
      voice?: string;
      speed?: number;
      generateAudio?: boolean;
    }
  ) => {
    const response = await fetch(API.chat(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify({
        message,
        session_id: options?.sessionId,
        voice: options?.voice || 'aria',
        speed: options?.speed || 0,
        generate_audio: options?.generateAudio ?? true,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to send message');
    }

    return response.json();
  };

  const textToSpeech = async (text: string, voice?: string, speed?: number) => {
    const response = await fetch(API.tts(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify({ text, voice, speed }),
    });

    if (!response.ok) {
      throw new Error('Failed to convert text to speech');
    }

    return response.json();
  };

  const getVoices = async () => {
    const response = await fetch(API.voices(), { mode: 'cors' });
    return response.json();
  };

  const getModels = async () => {
    const response = await fetch(API.models(), { mode: 'cors' });
    return response.json();
  };

  const getAudioUrl = (audioId: string) => API.audio(audioId);

  return {
    sendMessage,
    textToSpeech,
    getVoices,
    getModels,
    getAudioUrl,
  };
}
