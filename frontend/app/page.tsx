'use client';

import Link from 'next/link';
import {
  ArrowRight,
  BrainCircuit,
  ChartNoAxesCombined,
  CheckCircle2,
  Cpu,
  Database,
  Droplet,
  Globe2,
  Leaf,
  Layers,
  ShieldCheck,
  Sparkles,
  Sprout,
  TrendingUp,
  Trees,
  Upload,
  Workflow,
  Zap,
} from 'lucide-react';

import { SiteFooter } from '@/components/sections/site-footer';
import { HeroSection } from '@/components/ui/hero-section-5';
import { Button } from '@/components/ui/button';

const stats = [
  { value: '706', label: 'Districts Modeled', helper: 'Pan-India coverage' },
  { value: '24 yrs', label: 'Historical Data', helper: 'IMD & ICRISAT telemetry' },
  { value: '<15ms', label: 'Inference Latency', helper: 'CPU-optimized RandomForest' },
  { value: '100%', label: 'Deterministic Audits', helper: 'Zero black-box hallucination' },
];

const featureCards = [
  {
    title: 'Multi-Criteria Crop Intelligence',
    description: 'Jointly optimize crop selection across predicted yield, market mandi price, climate stability, and soil suitability.',
    image:
      'https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=1200&q=80',
  },
  {
    title: 'Climate Stress Simulation',
    description: 'Simulate drought, excess rainfall, and heatwave anomalies to discover climate-resilient crop alternatives before sowing.',
    image:
      'https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=1200&q=80',
  },
  {
    title: 'Sustainability Impact Scoring',
    description: 'Evaluate water demand reduction, fertilizer chemical load, and carbon footprint proxies derived from agronomic baselines.',
    image:
      'https://images.unsplash.com/photo-1471193945509-9ad0617afabf?auto=format&fit=crop&w=1200&q=80',
  },
];

const pipelineSteps = [
  {
    step: '01',
    title: 'Geographic Context Ingestion',
    desc: 'Takes district name, seasonal calendar, and plot area to retrieve historical climate normals and soil telemetry.',
    icon: Globe2,
  },
  {
    step: '02',
    title: 'Dual ML Regression Engine',
    desc: 'Runs 8-feature RandomForest yield prediction and 3-feature AGMARKNET mandi price forecasting in parallel.',
    icon: Cpu,
  },
  {
    step: '03',
    title: 'Climate Stress Simulation',
    desc: 'Injects rainfall deltas and temperature anomalies to model yield degradation under extreme weather scenarios.',
    icon: Zap,
  },
  {
    step: '04',
    title: 'Multi-Criteria Synthesis',
    desc: 'Scores all crop candidates on Yield (40%), Mandi Revenue (30%), Climate Stability (20%), and Soil Match (10%).',
    icon: Sparkles,
  },
];

const pillars = [
  {
    icon: BrainCircuit,
    title: 'Dual ML Regression Engine',
    description: 'RandomForest models trained on 24 years of ICRISAT crop records, IMD climate data, and AGMARKNET wholesale prices.',
  },
  {
    icon: ChartNoAxesCombined,
    title: 'Transparent Decision Metrics',
    description: 'Revenue forecasts, risk classifications (Low/Med/High), and water conservation percentages presented clearly.',
  },
  {
    icon: ShieldCheck,
    title: 'Stateless & CPU-Efficient',
    description: 'Sub-15ms inference latency running on standard CPUs with no expensive GPU or database overhead.',
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <HeroSection />

      {/* Stats Counter Ribbon */}
      <section className="border-y border-border/50 bg-card/60 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-8 lg:px-12">
          <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
            {stats.map((item) => (
              <div key={item.label} className="text-center sm:text-left">
                <p className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
                  {item.value}
                </p>
                <p className="mt-1 text-sm font-semibold text-foreground">{item.label}</p>
                <p className="text-xs text-muted-foreground">{item.helper}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Capabilities */}
      <section className="mx-auto max-w-7xl px-6 py-24 lg:px-12">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary">
              Core Capabilities
            </p>
            <h2 className="mt-4 text-4xl tracking-tight md:text-5xl text-foreground">
              Data-driven agriculture for profitability and ecological balance.
            </h2>
          </div>
          <p className="max-w-xl text-muted-foreground">
            KrishiMind SustainAI provides district-level crop recommendations for 706 Indian districts, combining empirical yield and price predictions with auditable sustainability impact metrics.
          </p>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          {featureCards.map((card) => (
            <article
              key={card.title}
              className="group overflow-hidden rounded-[2rem] border border-border/60 bg-card/90 shadow-xl shadow-lime-900/5 transition-all duration-300 hover:-translate-y-1 dark:shadow-black/20"
            >
              <img
                src={card.image}
                alt={card.title}
                className="h-64 w-full object-cover transition duration-500 group-hover:scale-105"
              />
              <div className="p-6">
                <h3 className="text-2xl font-bold text-foreground">{card.title}</h3>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">{card.description}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Interactive Optimization Pipeline */}
      <section className="mx-auto max-w-7xl px-6 pb-24 lg:px-12">
        <div className="rounded-[2.5rem] border border-border/60 bg-card/90 p-8 shadow-xl shadow-lime-900/5 dark:shadow-black/20 lg:p-12">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary">
              System Pipeline
            </p>
            <h2 className="mt-3 text-3xl font-extrabold tracking-tight text-foreground md:text-4xl">
              How the Multi-Factor Engine Optimizes Recommendations
            </h2>
            <p className="mt-3 text-sm text-muted-foreground">
              A 4-stage deterministic and machine learning workflow executing in sub-15ms.
            </p>
          </div>

          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {pipelineSteps.map((step) => {
              const Icon = step.icon;
              return (
                <div
                  key={step.step}
                  className="relative rounded-2xl border border-border/60 bg-background/70 p-6 transition-all hover:border-primary/40"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-primary">
                      Step {step.step}
                    </span>
                    <div className="rounded-full bg-primary/10 p-2 text-primary">
                      <Icon className="size-4" />
                    </div>
                  </div>
                  <h3 className="mt-4 text-lg font-bold text-foreground">{step.title}</h3>
                  <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{step.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Production Engineering Highlights */}
      <section className="mx-auto max-w-7xl px-6 pb-24 lg:px-12">
        <div className="rounded-[2.5rem] border border-border/60 bg-slate-950 p-8 text-white shadow-2xl shadow-lime-950/10 md:p-12">
          <div className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-lime-300/70">
                Why this frontend works
              </p>
              <h2 className="mt-4 text-4xl tracking-tight md:text-5xl">
                Designed for agricultural decisions, not just screenshots.
              </h2>
              <p className="mt-4 max-w-xl text-sm leading-7 text-slate-300">
                The interface keeps the polished visual language you added, but re-centers
                the actions, content, and summaries around KrishiMind’s real backend capabilities.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button asChild size="lg" className="rounded-full">
                  <Link href="/analyze">
                    Open Analyzer
                    <ArrowRight className="ml-2 size-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="rounded-full border-white/20 bg-transparent text-white hover:bg-white/10 hover:text-white">
                  <Link href="/about">Read Architecture</Link>
                </Button>
              </div>
            </div>
            <div className="grid gap-4">
              {pillars.map((item) => (
                <div key={item.title} className="rounded-[1.75rem] border border-white/10 bg-white/5 p-5">
                  <item.icon className="size-6 text-lime-300" />
                  <p className="mt-4 text-xl font-semibold">{item.title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Final Feature Summary */}
      <section className="mx-auto max-w-7xl px-6 pb-24 lg:px-12">
        <div className="grid gap-6 md:grid-cols-3">
          {[
            {
              icon: Trees,
              title: 'Crop intelligence',
              text: 'District, season, area, and climate scenario inputs map directly to the production crop-plan backend.',
            },
            {
              icon: Upload,
              title: 'Climate Resilience',
              text: 'Simulate extreme monsoon failures or heatwaves to evaluate how crop rankings shift.',
            },
            {
              icon: ChartNoAxesCombined,
              title: 'Actionable outputs',
              text: 'Users get ranked crops, risk, revenue, and environmental metrics in one place.',
            },
          ].map((item) => (
            <div key={item.title} className="rounded-[2rem] border border-border/60 bg-card/90 p-6 shadow-xl shadow-lime-900/5 dark:shadow-black/20">
              <item.icon className="size-6 text-primary" />
              <h3 className="mt-4 text-2xl font-bold text-foreground">{item.title}</h3>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
