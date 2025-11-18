import { Button } from '@/components/ui/button';
import { ArrowRight, Play, Star, Users, Zap } from 'lucide-react';

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-background via-background to-muted/20 py-20 lg:py-32">
      <div className="container relative z-10 mx-auto px-4 text-center">
        {/* Badge */}
        <div className="mb-8 inline-flex items-center rounded-full border bg-background/50 px-4 py-2 text-sm font-medium text-muted-foreground backdrop-blur-sm">
          <Star className="mr-2 h-4 w-4 fill-primary text-primary" />
          Built with Next.js 14 & Modern Best Practices
        </div>

        {/* Main Heading */}
        <h1 className="mx-auto mb-6 max-w-4xl text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl xl:text-7xl">
          Modern{' '}
          <span className="text-gradient">Next.js</span>{' '}
          Development Platform
        </h1>

        {/* Subtitle */}
        <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground sm:text-xl lg:text-2xl">
          Enterprise-grade Next.js solution built with TypeScript, Tailwind CSS, and modern UI frameworks. 
          Follows best practices for performance, security, and maintainability.
        </p>

        {/* CTA Buttons */}
        <div className="mb-12 flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-6">
          <Button size="lg" className="group">
            Get Started
            <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Button>
          <Button variant="outline" size="lg" className="group">
            <Play className="mr-2 h-4 w-4" />
            Watch Demo
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div className="flex flex-col items-center">
            <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Zap className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold text-foreground">10x</div>
            <div className="text-sm text-muted-foreground">Faster Development</div>
          </div>
          
          <div className="flex flex-col items-center">
            <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Star className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold text-foreground">99.9%</div>
            <div className="text-sm text-muted-foreground">Uptime</div>
          </div>
          
          <div className="flex flex-col items-center">
            <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Users className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold text-foreground">50K+</div>
            <div className="text-sm text-muted-foreground">Developers</div>
          </div>
        </div>
      </div>

      {/* Background Elements */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute left-1/4 top-1/4 h-64 w-64 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute right-1/4 bottom-1/4 h-64 w-64 rounded-full bg-secondary/5 blur-3xl" />
      </div>
    </section>
  );
}















