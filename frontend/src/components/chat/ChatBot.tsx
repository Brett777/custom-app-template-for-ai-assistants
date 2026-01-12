import { useState, useRef, useEffect } from 'react'
import { apiUrl } from '@/lib/basePath'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

/**
 * Message in the chat conversation.
 */
interface Message {
  role: 'user' | 'assistant'
  content: string
}

/**
 * Agent configuration status from the backend.
 */
interface AgentStatus {
  configured: boolean
  deployment_id_set: boolean
  api_token_set: boolean
  endpoint: string
}

/**
 * ChatBot component for interacting with DataRobot Agent Deployments.
 *
 * This component provides a chat interface that communicates with the
 * backend /api/v1/agent/chat endpoint, which proxies requests to the
 * configured DataRobot Agent Deployment.
 *
 * Example usage:
 * ```tsx
 * import { ChatBot } from '@/components/chat/ChatBot'
 *
 * function App() {
 *   return <ChatBot />
 * }
 * ```
 */
export function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Check agent configuration status on mount
  useEffect(() => {
    fetch(apiUrl('/api/v1/agent/status'))
      .then(res => res.json())
      .then(setAgentStatus)
      .catch(() => setAgentStatus(null))
  }, [])

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  /**
   * Send a message to the agent.
   */
  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = { role: 'user', content: input.trim() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(apiUrl('/api/v1/agent/chat'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          stream: false,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Failed to get response')
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.content,
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Handle Enter key press to send message.
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  /**
   * Clear chat history.
   */
  const clearChat = () => {
    setMessages([])
    setError(null)
  }

  // Show configuration warning if agent is not set up
  const showConfigWarning = agentStatus && !agentStatus.configured

  return (
    <Card className="w-full max-w-2xl mx-auto h-[600px] flex flex-col">
      <CardHeader className="flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle>Agent Chat</CardTitle>
          {messages.length > 0 && (
            <Button variant="outline" size="sm" onClick={clearChat}>
              Clear
            </Button>
          )}
        </div>
        {showConfigWarning && (
          <div className="mt-2 p-2 bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 rounded text-sm">
            Agent not configured. Set AGENT_DEPLOYMENT_ID and DATAROBOT_API_TOKEN.
          </div>
        )}
      </CardHeader>

      <CardContent className="flex-1 flex flex-col overflow-hidden p-4 pt-0">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto pr-2 space-y-4">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center">
              <p className="text-muted-foreground text-center">
                {showConfigWarning
                  ? 'Configure the agent deployment to start chatting'
                  : 'Start a conversation with the agent'}
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <p className="whitespace-pre-wrap break-words">{message.content}</p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-4 py-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-current rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.1s]" />
                  <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.2s]" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-2 p-3 bg-destructive/10 text-destructive rounded-lg text-sm flex-shrink-0">
            {error}
          </div>
        )}

        {/* Input Area */}
        <div className="mt-4 flex gap-2 flex-shrink-0">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={isLoading || showConfigWarning}
            className="flex-1 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          />
          <Button
            onClick={sendMessage}
            disabled={isLoading || !input.trim() || showConfigWarning}
          >
            Send
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default ChatBot
