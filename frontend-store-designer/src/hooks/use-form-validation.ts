import { useState, useCallback } from 'react'
import * as validators from '@/utils/validation'

type Validator = (value: unknown) => boolean | string

interface ValidationRule {
  validator: Validator
  message?: string
}

interface ValidationRules {
  [key: string]: ValidationRule[]
}

export function useFormValidation<T extends Record<string, unknown>>(
  rules: ValidationRules
) {
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({})

  const validate = useCallback(
    (values: T): boolean => {
      const newErrors: Partial<Record<keyof T, string>> = {}

      Object.keys(rules).forEach((key) => {
        const fieldRules = rules[key]
        const value = values[key as keyof T]

        for (const rule of fieldRules) {
          const result = rule.validator(value)
          if (result !== true) {
            newErrors[key as keyof T] =
              typeof result === 'string' ? result : rule.message || 'Invalid value'
            break
          }
        }
      })

      setErrors(newErrors)
      return Object.keys(newErrors).length === 0
    },
    [rules]
  )

  const clearErrors = useCallback(() => {
    setErrors({})
  }, [])

  const setError = useCallback((field: keyof T, message: string) => {
    setErrors((prev) => ({ ...prev, [field]: message }))
  }, [])

  return { errors, validate, clearErrors, setError }
}

export { validators }


