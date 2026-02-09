import { useState, useEffect } from 'react'
import { storage } from '@/utils/storage'
import { STORAGE_KEYS } from '@/utils/constants'

interface Preferences {
  theme?: 'light' | 'dark'
  language?: string
  notifications?: boolean
}

export function usePreferences() {
  const [preferences, setPreferences] = useState<Preferences>(() =>
    storage.get<Preferences>(STORAGE_KEYS.PREFERENCES) || {}
  )

  useEffect(() => {
    storage.set(STORAGE_KEYS.PREFERENCES, preferences)
  }, [preferences])

  const updatePreferences = (updates: Partial<Preferences>) => {
    setPreferences((prev) => ({ ...prev, ...updates }))
  }

  return { preferences, updatePreferences }
}


