'use client';

import Link from 'next/link';
import { Cpu, Database, PanelTop, Workflow } from 'lucide-react';


import { SiteHeader } from '@/components/sections/site-header';
import { Button } from '@/components/ui/button';
import { SiteFooter } from '@/components/sections/site-footer';

const stack = [
  {
    icon: PanelTop,
    title: 'Next.js 15 App Router',
    description: 'Modern React 19 UI with TypeScript, Tailwind CSS, and server-side API proxy route handlers.',
  },
  {
    icon: Workflow,
    title: 'Multi-Criteria Optimizer',
    description: 'Composite scoring engine balancing predicted yield, mandi prices, climate stability, and soil match.',
  },
  {
    icon: Cpu,
    title: 'Dual Machine Learning Models',
    description: 'Trained RandomForest regressors for crop yield (R²=0.85) and commodity wholesale pricing (R²=0.96).',
  },
  {
    icon: Database,
    title: 'Deterministic Sustainability Engine',
    description: 'FAO agronomic baseline proxy calculators for water savings, chemical fertilizer load, and carbon footprint.',
  },
];

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-12">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary">
            System Architecture
          </p>
          <h1 className="mt-4 text-4xl font-extrabold tracking-tight md:text-5xl">
            Engineering for sustainable agricultural resilience.
          </h1>
          <p className="mt-4 text-base leading-relaxed text-muted-foreground">
            KrishiMind SustainAI couples classical machine learning regression with deterministic agronomic proxy calculations to deliver sub-15ms decision intelligence without expensive cloud infrastructure.
          </p>
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-2">
          {stack.map((item) => (
            <div key={item.title} className="rounded-[2rem] border border-border/60 bg-card/90 p-6 shadow-xl shadow-lime-900/5 dark:shadow-black/20">
              <item.icon className="size-6 text-primary" />
              <h2 className="mt-5 text-2xl font-bold text-foreground">{item.title}</h2>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{item.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 rounded-[2.5rem] border border-border/60 bg-slate-950 p-8 text-white md:p-12">
          <h2 className="text-3xl font-bold">Local & Cloud Execution</h2>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300">
            The FastAPI backend runs on port 8000 using Uvicorn, loading serialized RandomForest models into resident memory at startup. The Next.js frontend proxies user requests via `/api/predict`, providing a responsive, state-of-the-art interface.
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
