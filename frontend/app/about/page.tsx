import Link from 'next/link';
import { Cpu, Database, PanelTop, Workflow } from 'lucide-react';

import { SiteHeader } from '@/components/sections/site-header';
import { Button } from '@/components/ui/button';
import { SiteFooter } from '@/components/sections/site-footer';

const stack = [
  {
    icon: PanelTop,
    title: 'Next.js App Router',
    description: 'Modern React frontend with TypeScript and Tailwind CSS as the main product UI.',
  },
  {
    icon: Workflow,
    title: 'shadcn-compatible structure',
    description: 'Reusable UI primitives live in `/components/ui` for scalable composition.',
  },
  {
    icon: Cpu,
    title: 'FastAPI + integrated inference',
    description: 'The analyzer proxies district inputs and optional image uploads into the unified crop-plan backend.',
  },
  {
    icon: Database,
    title: 'Production-oriented shell',
    description: 'The UI now supports landing, analysis, disease catalog, and architecture pages for the full workflow.',
  },
];

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-12">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary">
            About the Build
          </p>
          <h1 className="mt-4 text-4xl tracking-tight md:text-5xl">
            The frontend now reflects the full KrishiMind product.
          </h1>
          <p className="mt-4 text-muted-foreground">
            The original repository already had crop-planning infrastructure and a separate disease module.
            This frontend now acts as the main shared interface for both capabilities.
          </p>
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-2">
          {stack.map((item) => (
            <div key={item.title} className="rounded-[2rem] border border-border/60 bg-white/90 p-6 shadow-xl shadow-lime-900/5">
              <item.icon className="size-6 text-primary" />
              <h2 className="mt-5 text-2xl">{item.title}</h2>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{item.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 rounded-[2rem] border border-border/60 bg-slate-950 p-8 text-white">
          <h2 className="text-3xl">Running the stack</h2>
          <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300">
            Start the FastAPI backend on port 8000, then launch the Next.js frontend from the
            `frontend` directory. The analyzer route saves uploaded images temporarily on the
            server, forwards `image_path` to the integrated backend, and cleans up afterward.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button asChild size="lg" className="rounded-full">
              <Link href="/analyze">Open Analyzer</Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="rounded-full border-white/20 bg-transparent text-white hover:bg-white/10 hover:text-white"
            >
              <Link href="/">Back Home</Link>
            </Button>
          </div>
        </div>
      </section>
      <SiteFooter />
    </div>
  );
}
