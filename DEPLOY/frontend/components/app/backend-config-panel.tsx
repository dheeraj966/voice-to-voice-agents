'use client';

import { useState } from 'react';
import { useBackendConnection } from '@/hooks/useBackend';

interface BackendConfigPanelProps {
  className?: string;
}

export function BackendConfigPanel({ className }: BackendConfigPanelProps) {
  const {
    status,
    connected,
    message,
    backendUrl,
    livekitUrl,
    ollamaAvailable,
    model,
    checkConnection,
    setBackendUrl,
    setLivekitUrl,
    resetBackendConfig,
  } = useBackendConnection();

  const [newBackendUrl, setNewBackendUrl] = useState(backendUrl);
  const [newLivekitUrl, setNewLivekitUrl] = useState(livekitUrl || '');
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSaveBackend = () => {
    if (newBackendUrl && newBackendUrl !== backendUrl) {
      setBackendUrl(newBackendUrl);
    }
  };

  const handleSaveLivekit = () => {
    if (newLivekitUrl && newLivekitUrl !== livekitUrl) {
      setLivekitUrl(newLivekitUrl);
    }
  };

  const statusColor = {
    checking: 'bg-yellow-500',
    connected: 'bg-green-500',
    disconnected: 'bg-red-500',
    error: 'bg-red-500',
  }[status];

  const statusIcon = {
    checking: '⏳',
    connected: '✅',
    disconnected: '❌',
    error: '⚠️',
  }[status];

  return (
    <div className={`rounded-lg border border-border bg-card p-4 ${className}`}>
      {/* Status Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className={`h-3 w-3 rounded-full ${statusColor}`} />
          <span className="font-medium">Backend Connection</span>
          <span className="text-xl">{statusIcon}</span>
        </div>
        <span className="text-muted-foreground">{isExpanded ? '▲' : '▼'}</span>
      </button>

      {/* Status Message */}
      <p className="mt-2 text-sm text-muted-foreground">{message}</p>
      
      {connected && (
        <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
          <span>Model: {model || 'Unknown'}</span>
          <span>Ollama: {ollamaAvailable ? '✅' : '❌'}</span>
        </div>
      )}

      {/* Expanded Config */}
      {isExpanded && (
        <div className="mt-4 space-y-4 border-t border-border pt-4">
          {/* Backend URL */}
          <div>
            <label className="mb-1 block text-sm font-medium">
              Backend URL (where your Python server runs)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={newBackendUrl}
                onChange={(e) => setNewBackendUrl(e.target.value)}
                placeholder="http://your-server-ip:5000"
                className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <button
                onClick={handleSaveBackend}
                className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
              >
                Save
              </button>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Examples: http://192.168.1.100:5000, https://your-server.railway.app
            </p>
          </div>

          {/* LiveKit URL */}
          <div>
            <label className="mb-1 block text-sm font-medium">
              LiveKit URL (for voice streaming)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={newLivekitUrl}
                onChange={(e) => setNewLivekitUrl(e.target.value)}
                placeholder="wss://your-project.livekit.cloud"
                className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <button
                onClick={handleSaveLivekit}
                className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
              >
                Save
              </button>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={checkConnection}
              className="rounded-md border border-input px-4 py-2 text-sm hover:bg-accent"
            >
              🔄 Test Connection
            </button>
            <button
              onClick={resetBackendConfig}
              className="rounded-md border border-input px-4 py-2 text-sm hover:bg-accent"
            >
              🔄 Reset to Defaults
            </button>
          </div>

          {/* Help Text */}
          <div className="rounded-md bg-muted p-3 text-xs">
            <p className="font-medium">How to connect:</p>
            <ol className="mt-2 list-inside list-decimal space-y-1">
              <li>Run the backend on your server: <code className="rounded bg-background px-1">python src/web_agent.py</code></li>
              <li>Find your server's IP address</li>
              <li>Enter the URL above (e.g., http://192.168.1.100:5000)</li>
              <li>Click Save - the page will reload</li>
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}
