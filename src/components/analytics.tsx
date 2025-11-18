'use client';

import { useEffect } from 'react';

export function Analytics() {
  useEffect(() => {
    // Analytics initialization can go here
    // Example: Google Analytics, Plausible, etc.
    
    if (process.env.NODE_ENV === 'production') {
      // Initialize production analytics
      console.log('Analytics initialized in production');
    }
  }, []);

  return null; // This component doesn't render anything
}





