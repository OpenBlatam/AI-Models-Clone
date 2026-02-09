'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { ErrorMessage } from '@/components/error-message'
import { useChatSession } from '@/hooks/use-chat'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Send, Loader2, Sparkles } from 'lucide-react'
import { useToast } from '@/components/ui/toast'
import { formatDate } from '@/lib/utils'
import type { ChatMessage } from '@/types'

export default function ChatPage() {
  const [message, setMessage] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const router = useRouter()
  const { showToast } = useToast()
  const {
    session,
    sendMessage,
    isSending,
    sendError,
    generateDesign,
    isGenerating,
    generateError,
  } = useChatSession()

  const error = sendError || generateError

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [session?.messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !isSending) {
      sendMessage(message)
      setMessage('')
    }
  }

  const handleGenerateDesign = () => {
    generateDesign(undefined, {
      onSuccess: (design) => {
        showToast('Diseño generado exitosamente', 'success')
        router.push(`/designs/${design.store_id}`)
      },
      onError: (error: Error) => {
        showToast(error.message || 'Error al generar diseño', 'error')
      },
    })
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <ErrorMessage
          message="Error al cargar el chat"
          onRetry={() => router.refresh()}
        />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Chat con IA - Diseñador de Locales
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[500px] overflow-y-auto mb-4 space-y-4 p-4 bg-gradient-to-b from-gray-50 to-white rounded-lg border">
            {!session && createSessionMutation.isPending && (
              <div className="flex justify-center items-center h-full">
                <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
              </div>
            )}

            {session?.messages.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <p className="mb-2">¡Hola! Soy tu asistente de diseño de locales.</p>
                <p>Pregúntame sobre tu tienda y te ayudaré a diseñarla.</p>
              </div>
            )}

            {session?.messages.map((msg: ChatMessage, idx: number) => (
              <div
                key={idx}
                className={`flex gap-2 ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[75%] rounded-lg p-3 shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-200'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  <p
                    className={`text-xs mt-1 ${
                      msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                    }`}
                  >
                    {formatDate(msg.timestamp)}
                  </p>
                </div>
              </div>
            ))}

            {isSending && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Describe tu local ideal..."
              disabled={isSending || !session}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
            />
            <Button
              type="submit"
              disabled={isSending || !session || !message.trim()}
            >
              {isSending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </form>

          {session && session.messages.length > 0 && (
            <div className="mt-4">
              <Button
                onClick={handleGenerateDesign}
                disabled={isGenerating}
                className="w-full"
                variant="outline"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generando diseño...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generar Diseño desde Chat
                  </>
                )}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

