'use client';

import { SiteHeader } from '@/components/sections/site-header';

import { AnalyzePanel } from '@/components/sections/analyze-panel';
import { SiteFooter } from '@/components/sections/site-footer';

export default function AnalyzePage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 pb-24 pt-12 lg:px-12">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary">
            Crop Decision Workspace
          </p>
          <h1 className="mt-4 text-4xl font-extrabold tracking-tight md:text-5xl">
            Sustainable Crop Planning & Scenario Optimization
          </h1>
          <p className="mt-4 text-base leading-relaxed text-muted-foreground">
            Evaluate regional crop suitability, predict harvest yields, estimate mandi revenues, and simulate climate stress anomalies to identify high-profit, water-efficient crops.
          </p>
        </div>
        <div className="mt-12">
          <AnalyzePanel />
        </div>
      </section>
      <SiteFooter />
    </div>
  );
}
