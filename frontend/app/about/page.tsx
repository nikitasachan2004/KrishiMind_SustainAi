'use client';

import Link from 'next/link';
import {
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  Cpu,
  Database,
  Droplet,
  Flame,
  Globe2,
  Layers,
  Leaf,
  PanelTop,
  Scale,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Sprout,
  TrendingUp,
  Workflow,
  Zap,
} from 'lucide-react';

import { SiteHeader } from '@/components/sections/site-header';
import { Button } from '@/components/ui/button';
import { SiteFooter } from '@/components/sections/site-footer';

const metrics = [
  { value: '706', label: 'Districts Modeled', desc: 'Pan-India coverage across all states' },
  { value: '<15ms', label: 'CPU Inference', desc: 'Sub-millisecond compute per crop candidate' },
  { value: 'R² 0.85 / 0.96', label: 'ML Accuracy', desc: 'Yield and mandi price model benchmarks' },
  { value: '99.8%', label: 'Lower Energy Load', desc: 'Zero GPU dependency, 100% Green AI' },
];

const pillars = [
  {
    icon: BrainCircuit,
    title: 'Dual ML Regression Engine',
    tag: 'Scikit-Learn • RandomForest',
    desc: 'Combines an 8-feature crop yield regressor (R²=0.8511) trained on 343,768 historical district-season records with a 3-feature AGMARKNET mandi price forecaster (R²=0.9635).',
    bullets: [
      'Models non-linear climate interactions (monsoon rainfall, heatwaves, GDD)',
      'Accurate yield estimation in tonnes/hectare per district',
      'Wholesale mandi price forecasts in ₹/tonne',
    ],
  },
  {
    icon: Droplet,
    title: 'Deterministic Sustainability Engine',
    tag: 'FAO Agronomic Baselines',
    desc: 'Uses zero black-box ML for ecological accounting. Every water, fertilizer, and carbon footprint estimate is calculated through auditable, deterministic agronomic formulas.',
    bullets: [
      'Estimates proxy water consumption (index-ha-days)',
      'Calculates water saved (%) against high-demand baseline crops like Rice',
      'Evaluates soil-adjusted fertilizer chemical load indices',
    ],
  },
  {
    icon: Zap,
    title: 'What-If Climate Stress Simulator',
    tag: 'Precipitation & Thermal Shocks',
    desc: 'Simulates acute climate shocks before seeds are purchased. Evaluates how crop yields and revenues shift under drought, surplus rainfall, and extreme heatwaves.',
    bullets: [
      'Rainfall anomaly injection (-50% to +50%)',
      'Temperature shift modeling (+0.5°C to +5.0°C)',
      'Identifies resilient crop alternatives before the season begins',
    ],
  },
  {
    icon: Scale,
    title: 'Multi-Criteria Decision Optimizer',
    tag: 'Weighted Multi-Objective',
    desc: 'Synthesizes competing agronomic and financial objectives into a balanced composite score (0.0 to 1.0) rather than maximizing yield in isolation.',
    bullets: [
      '40% Weight: Normalized Predicted Yield',
      '30% Weight: Expected Mandi Market Revenue',
      '20% Weight: Historical Climate Stability Factor',
      '10% Weight: Regional Soil Micronutrient Match',
    ],
  },
];

const dataSources = [
  {
    name: 'ICRISAT Data Repository',
    coverage: '343,768 records (1997–2020)',
    role: 'Historical crop production, acreage, and yield statistics across 54 crop varieties.',
  },
  {
    name: 'India Meteorological Department (IMD)',
    coverage: '23,434 weather telemetry records',
    role: 'Daily gridded rainfall anomalies, thermal indices, heatwave event counts, and growing degree days.',
  },
  {
    name: 'Soil Health Card Portal',
    coverage: 'National district database',
    role: 'Soil micronutrient profiles (Zn, Fe, Cu, Mn, B, S) and composite Soil Quality Index (SQI).',
  },
  {
    name: 'AGMARKNET Agricultural Marketing Network',
    coverage: 'Wholesale market transactions',
    role: 'District mandi pricing, seasonal wholesale rate fluctuations, and commodity arrival volumes.',
  },
];

const greenAiComparison = [
  {
    feature: 'Compute Requirement',
    krishiMind: 'Commodity CPU (< 256MB RAM)',
    traditional: 'High-end GPUs (16GB–80GB VRAM)',
  },
  {
    feature: 'Inference Latency',
    krishiMind: '< 15 milliseconds',
    traditional: '1.5 – 5.0 seconds (LLM generation)',
  },
  {
    feature: 'Hallucination Risk',
    krishiMind: '0% (Auditable deterministic math)',
    traditional: 'Non-zero (Stochastic LLM hallucination)',
  },
  {
    feature: 'Operational Energy Footprint',
    krishiMind: '~0.0001 kWh per query',
    traditional: '~0.05 – 0.1 kWh per query',
  },
];

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />

      {/* Hero Header */}
      <section className="mx-auto max-w-7xl px-6 pt-16 pb-12 lg:px-12">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-card/80 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-primary shadow-sm backdrop-blur">
            <Sparkles className="size-3.5" />
            Sustainable AI & Green Tech
          </div>
          <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl md:text-6xl">
            Engineering intelligence for agricultural resilience.
          </h1>
          <p className="mt-6 text-lg leading-relaxed text-muted-foreground">
            KrishiMind SustainAI replaces intuition and blanket inputs with multi-criteria optimization. By combining 24 years of empirical Indian agricultural records with deterministic resource accounting, we deliver fast, auditable crop advisory without expensive cloud infrastructure.
          </p>
        </div>

        {/* Metric Cards */}
        <div className="mt-12 grid grid-cols-2 gap-4 md:grid-cols-4">
          {metrics.map((item) => (
            <div
              key={item.label}
              className="rounded-2xl border border-border/60 bg-card/90 p-5 shadow-lg shadow-lime-900/5 dark:shadow-black/20"
            >
              <p className="text-3xl font-extrabold tracking-tight text-foreground md:text-4xl">
                {item.value}
              </p>
              <p className="mt-1 text-sm font-bold text-foreground">{item.label}</p>
              <p className="mt-1 text-xs text-muted-foreground">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Core Architectural Pillars */}
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-12">
        <div className="max-w-2xl">
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-primary">
            System Pillars
          </p>
          <h2 className="mt-3 text-3xl font-extrabold tracking-tight text-foreground md:text-4xl">
            How the Technology Works
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            A look under the hood at our dual regression engine, climate stress simulator, and sustainability logic.
          </p>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-2">
          {pillars.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.title}
                className="flex flex-col justify-between rounded-[2rem] border border-border/60 bg-card/90 p-8 shadow-xl shadow-lime-900/5 transition hover:border-primary/40 dark:shadow-black/20"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div className="rounded-2xl bg-primary/10 p-3 text-primary">
                      <Icon className="size-6" />
                    </div>
                    <span className="rounded-full bg-secondary px-3 py-1 text-[11px] font-semibold text-muted-foreground">
                      {item.tag}
                    </span>
                  </div>
                  <h3 className="mt-5 text-2xl font-bold text-foreground">{item.title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{item.desc}</p>

                  <div className="mt-6 space-y-2 border-t border-border/40 pt-4">
                    {item.bullets.map((bullet) => (
                      <div key={bullet} className="flex items-start gap-2 text-xs text-foreground">
                        <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-primary" />
                        <span>{bullet}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Green AI Efficiency Comparison */}
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-12">
        <div className="rounded-[2.5rem] border border-border/60 bg-slate-950 p-8 text-white shadow-2xl shadow-lime-950/10 md:p-12">
          <div className="max-w-2xl">
            <span className="rounded-full bg-emerald-500/20 px-3.5 py-1 text-xs font-semibold uppercase tracking-wider text-emerald-300">
              Sustainable AI Architecture
            </span>
            <h2 className="mt-4 text-3xl font-extrabold tracking-tight md:text-4xl">
              Why We Chose Tree Ensembles Over Generative LLMs
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-300">
              While generative LLMs are popular, deploying them for tabular agricultural prediction introduces high compute costs, GPU power consumption, and hallucination risks. KrishiMind achieves superior numeric precision while consuming $99.8\%$ less energy.
            </p>
          </div>

          <div className="mt-8 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-white/10 text-slate-400">
                  <th className="py-3 pr-4 font-semibold">Evaluation Criteria</th>
                  <th className="py-3 px-4 font-semibold text-emerald-400">KrishiMind SustainAI</th>
                  <th className="py-3 pl-4 font-semibold">Standard LLM / GPU Stack</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {greenAiComparison.map((row) => (
                  <tr key={row.feature}>
                    <td className="py-3.5 pr-4 font-medium text-slate-300">{row.feature}</td>
                    <td className="py-3.5 px-4 font-bold text-emerald-300">{row.krishiMind}</td>
                    <td className="py-3.5 pl-4 text-slate-400">{row.traditional}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Data Lineage & Training Foundations */}
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-12">
        <div className="max-w-2xl">
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-primary">
            Data Lineage
          </p>
          <h2 className="mt-3 text-3xl font-extrabold tracking-tight text-foreground md:text-4xl">
            Empirical Datasets & Sources
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            Zero synthetic data was generated for model training. All models originate from validated governmental and scientific archives.
          </p>
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {dataSources.map((source) => (
            <div
              key={source.name}
              className="rounded-2xl border border-border/60 bg-card/90 p-6 shadow-sm dark:shadow-black/20"
            >
              <div className="flex items-center justify-between">
                <span className="text-base font-bold text-foreground">{source.name}</span>
                <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-[11px] font-semibold text-primary">
                  {source.coverage}
                </span>
              </div>
              <p className="mt-3 text-xs leading-relaxed text-muted-foreground">{source.role}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Disclosures & Regulatory Context */}
      <section className="mx-auto max-w-7xl px-6 pb-24 lg:px-12">
        <div className="rounded-2xl border border-border/60 bg-card/80 p-8 shadow-md">
          <div className="flex items-start gap-3">
            <ShieldAlert className="mt-1 size-5 shrink-0 text-amber-600 dark:text-amber-400" />
            <div>
              <h3 className="text-lg font-bold text-foreground">
                Technical Governance & Responsible AI Disclosures
              </h3>
              <div className="mt-3 space-y-2 text-xs leading-relaxed text-muted-foreground">
                <p>
                  <strong>1. District Granularity:</strong> Recommendations are aggregated at the district administrative level. No field-specific GPS coordinates or micro-plots are inferred.
                </p>
                <p>
                  <strong>2. Sustainability Proxies:</strong> Water savings, fertilizer indices, and carbon scores are comparative decision-support proxies derived from FAO agronomic literature, not direct on-field physical sensor readings.
                </p>
                <p>
                  <strong>3. Inference-Only Architecture:</strong> Models are loaded into resident memory at server startup. No continuous online retraining or external data harvesting occurs during inference.
                </p>
              </div>

              <div className="mt-6 flex flex-wrap gap-3">
                <Button asChild size="lg" className="rounded-full px-6 shadow-md shadow-primary/20">
                  <Link href="/analyze">
                    Launch Crop Optimizer
                    <ArrowRight className="ml-2 size-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="rounded-full px-6">
                  <Link href="/">Back to Home</Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
