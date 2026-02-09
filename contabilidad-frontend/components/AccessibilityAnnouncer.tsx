'use client';

import { useEffect, useState } from 'react';

interface AccessibilityAnnouncerProps {
  message: string | null;
  priority?: 'polite' | 'assertive';
}

export function AccessibilityAnnouncer({
  message,
  priority = 'polite',
}: AccessibilityAnnouncerProps) {
  const [announcement, setAnnouncement] = useState<string | null>(null);

  useEffect(() => {
    if (message) {
      setAnnouncement(message);
      // Limpiar después de que el screen reader lo lea
      const timer = setTimeout(() => setAnnouncement(null), 1000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  return (
    <div
      role="status"
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  );
}














