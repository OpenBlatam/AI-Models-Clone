import { TrendingUp, Users, Code, Zap } from 'lucide-react';

const stats = [
  {
    icon: Code,
    value: '100K+',
    label: 'Lines of Code',
    description: 'Well-tested and documented',
    change: '+15%',
    changeType: 'positive' as const,
  },
  {
    icon: Users,
    value: '10K+',
    label: 'Active Users',
    description: 'Growing community',
    change: '+25%',
    changeType: 'positive' as const,
  },
  {
    icon: Zap,
    value: '99.9%',
    label: 'Uptime',
    description: 'Reliable performance',
    change: '+0.1%',
    changeType: 'positive' as const,
  },
  {
    icon: TrendingUp,
    value: '50+',
    label: 'Features',
    description: 'Comprehensive toolkit',
    change: '+5',
    changeType: 'positive' as const,
  },
];

export function StatsSection() {
  return (
    <section className="section-padding bg-background">
      <div className="container">
        {/* Section Header */}
        <div className="mx-auto mb-16 max-w-3xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            Platform Statistics
          </h2>
          <p className="text-lg text-muted-foreground">
            Real numbers that demonstrate our commitment to quality and performance.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="group relative overflow-hidden rounded-xl border bg-background p-6 text-center transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
            >
              {/* Icon */}
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <stat.icon className="h-8 w-8 text-primary" />
              </div>

              {/* Value */}
              <div className="mb-2 text-3xl font-bold text-foreground">
                {stat.value}
              </div>

              {/* Label */}
              <div className="mb-2 text-lg font-semibold text-foreground">
                {stat.label}
              </div>

              {/* Description */}
              <div className="mb-3 text-sm text-muted-foreground">
                {stat.description}
              </div>

              {/* Change Indicator */}
              <div className="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-800 dark:bg-green-900/20 dark:text-green-400">
                <TrendingUp className="mr-1 h-3 w-3" />
                {stat.change}
              </div>

              {/* Hover Effect */}
              <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="mt-16 rounded-xl border bg-muted/30 p-8 text-center">
          <h3 className="mb-4 text-2xl font-bold text-foreground">
            Continuously Improving
          </h3>
          <p className="mx-auto max-w-2xl text-muted-foreground">
            Our platform is constantly evolving with regular updates, security patches, 
            and new features based on community feedback and industry best practices.
          </p>
        </div>
      </div>
    </section>
  );
}















