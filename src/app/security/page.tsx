import { Metadata } from 'next';
import SecurityDashboard from '@/components/security/SecurityDashboard';

export const metadata: Metadata = {
  title: 'Security Dashboard | Ultimate Security System',
  description: 'Real-time security monitoring and analysis dashboard',
  keywords: ['security', 'dashboard', 'monitoring', 'threat detection', 'compliance'],
};

export default function SecurityPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <SecurityDashboard />
      </div>
    </div>
  );
}








