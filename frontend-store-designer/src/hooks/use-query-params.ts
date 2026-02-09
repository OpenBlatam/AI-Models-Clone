import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { getQueryParam, setQueryParam, removeQueryParam } from '@/utils/url'

export function useQueryParams() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const getParam = (key: string): string | null => {
    return searchParams.get(key)
  }

  const setParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString())
    params.set(key, value)
    router.push(`?${params.toString()}`)
  }

  const removeParam = (key: string) => {
    const params = new URLSearchParams(searchParams.toString())
    params.delete(key)
    router.push(`?${params.toString()}`)
  }

  const getAllParams = (): Record<string, string> => {
    const result: Record<string, string> = {}
    searchParams.forEach((value, key) => {
      result[key] = value
    })
    return result
  }

  return { getParam, setParam, removeParam, getAllParams }
}


