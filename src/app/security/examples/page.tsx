import { Metadata } from 'next';
import SecurityExamplesDemo from '@/components/security/security-examples-demo';

export const metadata: Metadata = {
  title: 'Security Examples | Ultimate Security System',
  description: 'Security usage examples, demos, and implementation guides',
  keywords: ['security', 'examples', 'demo', 'implementation', 'guide', 'tutorial'],
};

export default function SecurityExamplesPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <SecurityExamplesDemo />
      </div>
    </div>
  );
}
