import { 
  Code2, 
  Shield, 
  Zap, 
  Smartphone, 
  Database, 
  GitBranch,
  TestTube,
  Palette
} from 'lucide-react';

const features = [
  {
    icon: Code2,
    title: 'TypeScript First',
    description: 'Built with TypeScript for type safety, better developer experience, and reduced runtime errors.',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
  },
  {
    icon: Shield,
    title: 'Security Focused',
    description: 'Implements security best practices including input validation, secure headers, and authentication.',
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
  },
  {
    icon: Zap,
    title: 'Performance Optimized',
    description: 'Next.js 14 with App Router, Server Components, and advanced optimization techniques.',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950/20',
  },
  {
    icon: Smartphone,
    title: 'Mobile First',
    description: 'Responsive design with mobile-first approach using Tailwind CSS and modern CSS features.',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
  },
  {
    icon: Database,
    title: 'Modern State Management',
    description: 'Zustand for global state and TanStack Query for server state management.',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
  },
  {
    icon: GitBranch,
    title: 'Git Hooks',
    description: 'Husky and lint-staged for pre-commit code quality checks and formatting.',
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
  },
  {
    icon: TestTube,
    title: 'Testing Ready',
    description: 'Jest, React Testing Library, and Playwright for comprehensive testing coverage.',
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-50 dark:bg-emerald-950/20',
  },
  {
    icon: Palette,
    title: 'Design System',
    description: 'Consistent UI components built with Radix UI and styled with Tailwind CSS.',
    color: 'text-pink-600',
    bgColor: 'bg-pink-50 dark:bg-pink-950/20',
  },
];

export function FeaturesSection() {
  return (
    <section className="section-padding bg-muted/30">
      <div className="container">
        {/* Section Header */}
        <div className="mx-auto mb-16 max-w-3xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            Built with Modern Best Practices
          </h2>
          <p className="text-lg text-muted-foreground">
            Our platform incorporates the latest technologies and development patterns 
            to ensure scalability, maintainability, and performance.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative overflow-hidden rounded-xl border bg-background p-6 transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
            >
              {/* Icon */}
              <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg ${feature.bgColor}`}>
                <feature.icon className={`h-6 w-6 ${feature.color}`} />
              </div>

              {/* Content */}
              <h3 className="mb-2 text-lg font-semibold text-foreground">
                {feature.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {feature.description}
              </p>

              {/* Hover Effect */}
              <div className="absolute inset-0 -z-10 bg-gradient-to-r from-primary/5 to-secondary/5 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <p className="mb-4 text-muted-foreground">
            Ready to build something amazing?
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <a
              href="#"
              className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
            >
              View Documentation
            </a>
            <a
              href="#"
              className="inline-flex items-center justify-center rounded-md border border-input bg-background px-6 py-3 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground"
            >
              GitHub Repository
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}















