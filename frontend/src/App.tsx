import { useEffect, useState } from 'react'
import { apiUrl } from '@/lib/basePath'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ChatBot } from '@/components/chat/ChatBot'

interface AppConfig {
  appTitle: string
  debug: boolean
}

interface HelloResponse {
  message: string
  timestamp: string
}

type View = 'home' | 'chat'

function App() {
  const [config, setConfig] = useState<AppConfig | null>(null)
  const [hello, setHello] = useState<HelloResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<View>('home')

  useEffect(() => {
    // Fetch configuration on mount
    fetch(apiUrl('/api/v1/config'))
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const handleHelloClick = async () => {
    try {
      const response = await fetch(apiUrl('/api/v1/hello'))
      const data = await response.json()
      setHello(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">
            {config?.appTitle || 'Hello World'}
          </h1>
          <p className="text-muted-foreground">
            DataRobot Custom Application Template
          </p>
          {config?.debug && (
            <Badge variant="outline">Debug Mode</Badge>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-center gap-2">
          <Button
            variant={view === 'home' ? 'default' : 'outline'}
            onClick={() => setView('home')}
          >
            Home
          </Button>
          <Button
            variant={view === 'chat' ? 'default' : 'outline'}
            onClick={() => setView('chat')}
          >
            Agent Chat
          </Button>
        </div>

        {/* Chat View */}
        {view === 'chat' && <ChatBot />}

        {/* Home View */}
        {view === 'home' && (
          <>
            {/* Main Card */}
            <Card>
              <CardHeader>
                <CardTitle>Welcome</CardTitle>
                <CardDescription>
                  This is a template for building DataRobot Custom Applications
                  with FastAPI backend and React frontend.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={handleHelloClick}>
                  Say Hello
                </Button>

                {hello && (
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="font-medium">{hello.message}</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      {new Date(hello.timestamp).toLocaleString()}
                    </p>
                  </div>
                )}

                {error && (
                  <div className="p-4 bg-destructive/10 text-destructive rounded-lg">
                    <p>Error: {error}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Features Card */}
            <Card>
              <CardHeader>
                <CardTitle>Features</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-primary rounded-full" />
                    FastAPI backend with automatic API documentation
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-primary rounded-full" />
                    React + TypeScript + Vite for fast development
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-primary rounded-full" />
                    Tailwind CSS + shadcn/ui for beautiful UI
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-primary rounded-full" />
                    DataRobot-ready with proper path handling
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-primary rounded-full" />
                    Agent Deployment integration for AI-powered chat
                  </li>
                </ul>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  )
}

export default App
