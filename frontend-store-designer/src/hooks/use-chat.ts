import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { ChatMessage } from '@/types'

export function useChatSession() {
  const [sessionId, setSessionId] = useState<string | null>(null)

  const createSessionMutation = useMutation({
    mutationFn: () => apiClient.createChatSession(),
    onSuccess: (data) => {
      setSessionId(data.session_id)
    },
  })

  useEffect(() => {
    if (!sessionId) {
      createSessionMutation.mutate()
    }
  }, [])

  const { data: session, refetch } = useQuery({
    queryKey: ['chat', sessionId],
    queryFn: () => apiClient.getChatSession(sessionId!),
    enabled: !!sessionId,
    refetchInterval: false,
  })

  const sendMessageMutation = useMutation({
    mutationFn: (content: string) =>
      apiClient.sendChatMessage(sessionId!, {
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      }),
    onSuccess: () => {
      refetch()
    },
  })

  const generateDesignMutation = useMutation({
    mutationFn: () => apiClient.generateDesignFromChat(sessionId!),
  })

  return {
    sessionId,
    session,
    sendMessage: sendMessageMutation.mutate,
    isSending: sendMessageMutation.isPending,
    sendError: sendMessageMutation.error,
    generateDesign: generateDesignMutation.mutate,
    isGenerating: generateDesignMutation.isPending,
    generateError: generateDesignMutation.error,
  }
}

