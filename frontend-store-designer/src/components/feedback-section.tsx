'use client'

import { useState } from 'react'
import { useFeedback, useAddFeedback } from '@/hooks/use-feedback'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/toast'
import { MessageSquare, Send, Loader2 } from 'lucide-react'

interface FeedbackSectionProps {
  storeId: string
}

export function FeedbackSection({ storeId }: FeedbackSectionProps) {
  const [feedback, setFeedback] = useState('')
  const { showToast } = useToast()
  const { data: feedbackData } = useFeedback(storeId)
  const addFeedbackMutation = useAddFeedback(storeId)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (feedback.trim()) {
      addFeedbackMutation.mutate(feedback, {
        onSuccess: () => {
          setFeedback('')
          showToast('Feedback enviado', 'success')
        },
        onError: (error: Error) => {
          showToast(error.message || 'Error al enviar feedback', 'error')
        },
      })
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5" />
          Feedback y Sugerencias
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Escribe tu feedback o sugerencia..."
            disabled={addFeedbackMutation.isPending}
          />
          <Button
            type="submit"
            disabled={addFeedbackMutation.isPending || !feedback.trim()}
          >
            {addFeedbackMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </form>

        {feedbackData && (
          <div className="mt-4 space-y-2">
            <h4 className="font-medium text-sm">Sugerencias:</h4>
            <div className="bg-gray-50 p-4 rounded-lg">
              <pre className="text-xs whitespace-pre-wrap">
                {JSON.stringify(feedbackData, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

