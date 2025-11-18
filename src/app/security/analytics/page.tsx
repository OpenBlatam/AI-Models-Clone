import { Metadata } from 'next';
import SecurityAnalytics from '@/components/security/security-analytics';

export const metadata: Metadata = {
  title: 'Security Analytics | Ultimate Security System',
  description: 'Comprehensive security analytics, threat intelligence, and performance insights',
  keywords: ['security', 'analytics', 'threat intelligence', 'performance', 'compliance', 'insights'],
};

export default function SecurityAnalyticsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <SecurityAnalytics />
      </div>
    </div>
  );
}

