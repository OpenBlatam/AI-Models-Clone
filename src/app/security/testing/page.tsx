import { Metadata } from 'next';
import AdvancedSecurityTesting from '@/components/security/advanced-security-testing';

export const metadata: Metadata = {
  title: 'Security Testing | Ultimate Security System',
  description: 'Advanced security testing, vulnerability assessment, and penetration testing tools',
  keywords: ['security', 'testing', 'vulnerability', 'penetration', 'assessment', 'compliance'],
};

export default function SecurityTestingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <AdvancedSecurityTesting />
      </div>
    </div>
  );
}
