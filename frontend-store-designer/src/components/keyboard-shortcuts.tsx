'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useKeyboardShortcut } from '@/hooks/use-keyboard-shortcut'

export function KeyboardShortcuts() {
  const router = useRouter()

  useKeyboardShortcut('ctrl+k', () => {
    router.push('/chat')
  })

  useKeyboardShortcut('ctrl+d', () => {
    router.push('/design')
  })

  useKeyboardShortcut('ctrl+/', () => {
    router.push('/dashboard')
  })

  return null
}


