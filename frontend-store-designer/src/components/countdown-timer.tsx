'use client'

import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface CountdownTimerProps {
  targetDate: Date | string
  onComplete?: () => void
  className?: string
}

export function CountdownTimer({
  targetDate,
  onComplete,
  className,
}: CountdownTimerProps) {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  })
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    const target = typeof targetDate === 'string' ? new Date(targetDate) : targetDate

    const updateTimer = () => {
      const now = new Date().getTime()
      const distance = target.getTime() - now

      if (distance < 0) {
        setIsComplete(true)
        if (onComplete) onComplete()
        return
      }

      setTimeLeft({
        days: Math.floor(distance / (1000 * 60 * 60 * 24)),
        hours: Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
        minutes: Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)),
        seconds: Math.floor((distance % (1000 * 60)) / 1000),
      })
    }

    updateTimer()
    const interval = setInterval(updateTimer, 1000)

    return () => clearInterval(interval)
  }, [targetDate, onComplete])

  if (isComplete) {
    return <div className={className}>Tiempo completado</div>
  }

  return (
    <div className={cn('flex gap-4', className)}>
      <div className="text-center">
        <div className="text-2xl font-bold">{timeLeft.days}</div>
        <div className="text-xs text-gray-500">Días</div>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold">{timeLeft.hours}</div>
        <div className="text-xs text-gray-500">Horas</div>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold">{timeLeft.minutes}</div>
        <div className="text-xs text-gray-500">Min</div>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold">{timeLeft.seconds}</div>
        <div className="text-xs text-gray-500">Seg</div>
      </div>
    </div>
  )
}


