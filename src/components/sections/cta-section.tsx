import { Button } from '@/components/ui/button';
import { ArrowRight, Github, BookOpen, MessageCircle } from 'lucide-react';

export function CTASection() {
  return (
    <section className="section-padding bg-gradient-to-br from-primary/5 via-background to-secondary/5">
      <div className="container">
        <div className="mx-auto max-w-4xl text-center">
          {/* Main CTA */}
          <h2 className="mb-6 text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            Ready to Build Something Amazing?
          </h2>
          
          <p className="mb-8 text-lg text-muted-foreground sm:text-xl">
            Join thousands of developers who are already building faster, more reliable, 
            and more maintainable applications with our modern Next.js platform.
          </p>

          {/* Primary CTA Buttons */}
          <div className="mb-12 flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-6">
            <Button size="lg" className="group">
              Get Started Now
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Button>
            <Button variant="outline" size="lg">
              View Documentation
            </Button>
          </div>

          {/* Secondary Actions */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            <a
              href="#"
              className="group flex flex-col items-center rounded-lg border bg-background p-6 transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <Github className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 font-semibold text-foreground">Open Source</h3>
              <p className="text-sm text-muted-foreground text-center">
                Contribute to our open-source project
              </p>
            </a>

            <a
              href="#"
              className="group flex flex-col items-center rounded-lg border bg-background p-6 transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <BookOpen className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 font-semibold text-foreground">Learn</h3>
              <p className="text-sm text-muted-foreground text-center">
                Explore our comprehensive guides
              </p>
            </a>

            <a
              href="#"
              className="group flex flex-col items-center rounded-lg border bg-background p-6 transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <MessageCircle className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 font-semibold text-foreground">Community</h3>
              <p className="text-sm text-muted-foreground text-center">
                Join our developer community
              </p>
            </a>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 rounded-xl border bg-background/50 p-8 backdrop-blur-sm">
            <h3 className="mb-4 text-xl font-semibold text-foreground">
              Trusted by Industry Leaders
            </h3>
            <p className="text-muted-foreground">
              Our platform powers applications for companies of all sizes, 
              from startups to Fortune 500 enterprises.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}















