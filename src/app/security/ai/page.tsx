import { Metadata } from 'next';
import AISecurityDashboard from '@/components/security/ai-security-dashboard';

export const metadata: Metadata = {
  title: 'AI Security | Ultimate Security System',
  description: 'Advanced AI-powered security with machine learning, deep learning, and predictive analytics',
  keywords: ['ai', 'security', 'machine learning', 'deep learning', 'threat detection', 'predictive analytics'],
};

export default function AISecurityPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <AISecurityDashboard />
      </div>
    </div>
  );
}
