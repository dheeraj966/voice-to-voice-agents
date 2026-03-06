// Backend API Configuration
// This file configures where the React frontend sends requests to

export interface BackendConfig {
  // The URL of your backend server (where web_agent.py runs)
  apiUrl: string;
  // WebSocket URL for real-time features (optional)
  wsUrl?: string;
  // LiveKit server URL
  livekitUrl?: string;
}

// Get backend URL from environment or use default
function getBackendUrl(): string {
  // Priority:
  // 1. Runtime config (set by user in browser localStorage)
  // 2. Environment variable (set at build time)
  // 3. Default localhost for development

  if (typeof window !== 'undefined') {
    const storedUrl = localStorage.getItem('VOICE_AI_BACKEND_URL');
    if (storedUrl) return storedUrl;
  }

  return process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';
}

function getLivekitUrl(): string {
  if (typeof window !== 'undefined') {
    const storedUrl = localStorage.getItem('VOICE_AI_LIVEKIT_URL');
    if (storedUrl) return storedUrl;
  }

  return process.env.NEXT_PUBLIC_LIVEKIT_URL || process.env.LIVEKIT_URL || 'ws://localhost:7880';
}

export const backendConfig: BackendConfig = {
  apiUrl: getBackendUrl(),
  wsUrl: getBackendUrl().replace('http', 'ws'),
  livekitUrl: getLivekitUrl(),
};

// Helper to update backend URL at runtime (useful for testing different backends)
export function setBackendUrl(url: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('VOICE_AI_BACKEND_URL', url);
    // Reload to apply new config
    window.location.reload();
  }
}

export function setLivekitUrl(url: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('VOICE_AI_LIVEKIT_URL', url);
    window.location.reload();
  }
}

// Clear stored URLs and use defaults
export function resetBackendConfig(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('VOICE_AI_BACKEND_URL');
    localStorage.removeItem('VOICE_AI_LIVEKIT_URL');
    window.location.reload();
  }
}

// API endpoints
export const API = {
  health: () => `${backendConfig.apiUrl}/health`,
  config: () => `${backendConfig.apiUrl}/api/config`,
  chat: () => `${backendConfig.apiUrl}/api/chat`,
  tts: () => `${backendConfig.apiUrl}/api/tts`,
  voices: () => `${backendConfig.apiUrl}/api/voices`,
  models: () => `${backendConfig.apiUrl}/api/models`,
  audio: (id: string) => `${backendConfig.apiUrl}/api/audio/${id}`,
  history: (sessionId: string) => `${backendConfig.apiUrl}/api/history/${sessionId}`,
  clear: (sessionId: string) => `${backendConfig.apiUrl}/api/clear/${sessionId}`,
  export: (sessionId: string) => `${backendConfig.apiUrl}/api/export/${sessionId}`,
};

export default backendConfig;
