'use client';

import { useEffect, useState } from 'react';

interface ConfettiProps {
  trigger: boolean;
  duration?: number;
}

export function Confetti({ trigger, duration = 3000 }: ConfettiProps) {
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (trigger) {
      setIsActive(true);
      const timer = setTimeout(() => setIsActive(false), duration);
      return () => clearTimeout(timer);
    }
  }, [trigger, duration]);

  if (!isActive) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {Array.from({ length: 50 }).map((_, i) => (
        <div
          key={i}
          className="absolute confetti-particle"
          style={{
            left: `${Math.random() * 100}%`,
            top: '-10px',
            animationDelay: `${Math.random() * 2}s`,
            animationDuration: `${2 + Math.random() * 2}s`,
            backgroundColor: [
              '#FF6B6B',
              '#4ECDC4',
              '#45B7D1',
              '#FFA07A',
              '#98D8C8',
              '#F7DC6F',
            ][Math.floor(Math.random() * 6)],
          }}
        />
      ))}
    </div>
  );
}














