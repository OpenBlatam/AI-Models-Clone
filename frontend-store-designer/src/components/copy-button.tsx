'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Copy, Check } from 'lucide-react'
import { useToast } from '@/components/ui/toast'

interface CopyButtonProps {
  text: string
  label?: string
  size?: 'sm' | 'md' | 'lg'
}

export function CopyButton({ text, label, size = 'sm' }: CopyButtonProps) {
  const [copied, setCopied] = useState(false)
  const { showToast } = useToast()

  const handleCopy = async () => {
    const { copyToClipboard } = await import('@/utils/clipboard')
    const success = await copyToClipboard(text)
    
    if (success) {
      setCopied(true)
      showToast('Copiado al portapapeles', 'success')
      setTimeout(() => setCopied(false), 2000)
    } else {
      showToast('Error al copiar', 'error')
    }
  }

  return (
    <Button
      variant="outline"
      size={size}
      onClick={handleCopy}
      className="gap-2"
    >
      {copied ? (
        <>
          <Check className="w-4 h-4" />
          {label || 'Copiado'}
        </>
      ) : (
        <>
          <Copy className="w-4 h-4" />
          {label || 'Copiar'}
        </>
      )}
    </Button>
  )
}

