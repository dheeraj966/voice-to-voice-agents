'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useBackendConnection, useBackendAPI } from '@/hooks/useBackend';
import { BackendConfigPanel } from '@/components/app/backend-config-panel';

export default function SetupPage() {
  const { status, connected, backendUrl, ollamaAvailable, model } = useBackendConnection();
  const api = useBackendAPI();
  const [testResult, setTestResult] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);

  const runTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await api.sendMessage('Hello, can you hear me?', {
        generateAudio: false,
      });
      setTestResult(`✅ Success! AI responded: "${result.text.substring(0, 100)}..."`);
    } catch (error) {
      setTestResult(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
    setTesting(false);
  };

  return (
    <main className="min-h-screen bg-background p-8">
      <div className="mx-auto max-w-2xl space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold">🎤 Voice AI Setup</h1>
          <p className="mt-2 text-muted-foreground">
            Connect this frontend to your backend server
          </p>
        </div>

        {/* Backend Config Panel */}
        <BackendConfigPanel />

        {/* Connection Status Details */}
        <div className="rounded-lg border border-border bg-card p-6">
          <h2 className="text-xl font-semibold">Connection Status</h2>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between">
              <span>Backend URL:</span>
              <code className="rounded bg-muted px-2 py-1 text-sm">{backendUrl}</code>
            </div>
            <div className="flex justify-between">
              <span>Status:</span>
              <span className={connected ? 'text-green-500' : 'text-red-500'}>
                {status === 'checking' ? '⏳ Checking...' : connected ? '✅ Connected' : '❌ Disconnected'}
              </span>
            </div>
            {connected && (
              <>
                <div className="flex justify-between">
                  <span>LLM Model:</span>
                  <span>{model || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Ollama:</span>
                  <span className={ollamaAvailable ? 'text-green-500' : 'text-yellow-500'}>
                    {ollamaAvailable ? '✅ Running' : '⚠️ Not Running'}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Test Chat */}
        {connected && (
          <div className="rounded-lg border border-border bg-card p-6">
            <h2 className="text-xl font-semibold">Test Connection</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Send a test message to verify the AI is responding
            </p>
            <button
              onClick={runTest}
              disabled={testing || !ollamaAvailable}
              className="mt-4 rounded-md bg-primary px-6 py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {testing ? '⏳ Testing...' : '🧪 Test AI Response'}
            </button>
            {testResult && (
              <div className="mt-4 rounded-md bg-muted p-3 text-sm">
                {testResult}
              </div>
            )}
          </div>
        )}

        {/* Next Steps */}
        <div className="rounded-lg border border-border bg-card p-6">
          <h2 className="text-xl font-semibold">Next Steps</h2>
          <div className="mt-4 space-y-4">
            {!connected ? (
              <div className="rounded-md bg-yellow-500/10 p-4 text-yellow-600">
                <p className="font-medium">⚠️ Backend not connected</p>
                <p className="mt-1 text-sm">
                  You need to run the Python backend on a server or your local machine.
                </p>
                <ol className="mt-3 list-inside list-decimal text-sm">
                  <li>Open a terminal on your server/PC</li>
                  <li>Navigate to <code>agent-starter-python</code> folder</li>
                  <li>Run: <code>python src/web_agent.py</code></li>
                  <li>Enter the server IP above</li>
                </ol>
              </div>
            ) : (
              <div className="rounded-md bg-green-500/10 p-4 text-green-600">
                <p className="font-medium">✅ Backend connected!</p>
                <p className="mt-1 text-sm">
                  You can now use the Voice AI. Go to the main app:
                </p>
                <Link
                  href="/"
                  className="mt-3 inline-block rounded-md bg-primary px-6 py-2 text-primary-foreground hover:bg-primary/90"
                >
                  🎤 Open Voice AI
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="rounded-lg border border-border bg-card p-6 text-sm">
          <h2 className="text-lg font-semibold">How This Works</h2>
          <div className="mt-4 space-y-3 text-muted-foreground">
            <p>
              <strong>Frontend (this website):</strong> Hosted on Netlify. Handles the UI and sends 
              requests to your backend.
            </p>
            <p>
              <strong>Backend (Python server):</strong> Runs on your computer or a cloud server. 
              Handles AI processing with Ollama.
            </p>
            <p>
              <strong>Connection:</strong> The frontend makes API calls to whatever backend URL you 
              configure. Your backend must have CORS enabled (it already does).
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
