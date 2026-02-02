import { useState, useEffect, useRef } from 'react'
import { useAppDispatch } from '@/app/hooks'
import { toggleAiPanel } from '../workspace/workspaceSlice'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { PastelBadge } from '@/components/shared/PastelBadge'
import { X, Send, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export function AIAssistant() {
  const dispatch = useAppDispatch()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm your AI assistant. I can help you design and create your trading card game.",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Simulate AI response (replace with actual API call)
    timeoutRef.current = setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I've received your message. In the full version, I'll help you with that!",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
      setIsLoading(false)
      timeoutRef.current = null
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b-2 border-wood-brown bg-white">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-heading text-lg text-text-primary">AI Assistant</h3>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => dispatch(toggleAiPanel())}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
        <PastelBadge color="yellow" className="bg-orange-primary text-white flex items-center gap-1 w-fit">
          <Sparkles className="w-3 h-3" />
          Creative Master AI
        </PastelBadge>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex",
              message.role === 'user' ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cn(
                "max-w-[80%] rounded-lg px-4 py-2",
                message.role === 'user'
                  ? "bg-orange-primary text-white"
                  : "bg-beige-light text-text-primary border-2 border-wood-brown"
              )}
            >
              <p className="text-sm">{message.content}</p>
              <p
                className={cn(
                  "text-xs mt-1",
                  message.role === 'user' ? "text-white/80" : "text-text-secondary"
                )}
              >
                {message.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-beige-light text-text-primary border-2 border-wood-brown rounded-lg px-4 py-2">
              <p className="text-sm">Thinking...</p>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t-2 border-wood-brown bg-white">
        <div className="space-y-2">
          <div className="flex gap-2">
            <Input
              placeholder="Ask AI for help..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="bg-orange-primary hover:bg-orange-hover text-white"
              size="icon"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setInput('Generate a card')}
            >
              Generate Card
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setInput('Create a rule')}
            >
              Create Rule
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setInput('Explain this flow')}
            >
              Explain Flow
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
