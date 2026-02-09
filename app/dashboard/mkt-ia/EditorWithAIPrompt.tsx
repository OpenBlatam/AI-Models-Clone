import './styles.scss'

import { EditorContent } from '@tiptap/react'
import React, { useState } from 'react'
import { useEditorAI } from '@/components/dashboard/mkt-ia/hooks/useEditorAI'
import { AIPromptControls } from '@/components/dashboard/mkt-ia/components/AIPromptControls'

export default function EditorWithAIPrompt() {
  const [prompt, setPrompt] = useState(
    "Write something about Tiptap Editor and include a list of it's core features",
  )
  const [shouldFormatResponse, setShouldFormatResponse] = useState(true)

  const { editor, generateText, isLoading, error } = useEditorAI({
    placeholder: 'Use the input above to generate content...',
  })

  if (!editor) {
    return null
  }

  const handleGenerate = async () => {
    await generateText(
      prompt,
      shouldFormatResponse ? 'rich-text' : 'plain-text',
      true
    )
  }

  return (
    <>
      <AIPromptControls
        prompt={prompt}
        onPromptChange={setPrompt}
        shouldFormatResponse={shouldFormatResponse}
        onFormatChange={setShouldFormatResponse}
        onGenerate={handleGenerate}
        loading={isLoading}
        error={error}
      />
      <EditorContent editor={editor} />
    </>
  )
} 