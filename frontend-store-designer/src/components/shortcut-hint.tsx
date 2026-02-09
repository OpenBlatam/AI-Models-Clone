'use client'

import { Keyboard } from 'lucide-react'
import { Button } from './ui/button'
import { Dialog } from './ui/dialog'
import { useState } from 'react'

const shortcuts = [
  { keys: ['Ctrl', 'K'], description: 'Abrir chat' },
  { keys: ['Ctrl', 'D'], description: 'Crear diseño' },
  { keys: ['Ctrl', '/'], description: 'Abrir dashboard' },
  { keys: ['Esc'], description: 'Cerrar modales' },
]

export function ShortcutHint() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(true)}
        className="gap-2"
      >
        <Keyboard className="w-4 h-4" />
        <span className="hidden md:inline">Atajos</span>
      </Button>

      <Dialog
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Atajos de Teclado"
      >
        <div className="space-y-4">
          {shortcuts.map((shortcut, idx) => (
            <div key={idx} className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{shortcut.description}</span>
              <div className="flex gap-1">
                {shortcut.keys.map((key, keyIdx) => (
                  <kbd
                    key={keyIdx}
                    className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded"
                  >
                    {key}
                  </kbd>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Dialog>
    </>
  )
}


