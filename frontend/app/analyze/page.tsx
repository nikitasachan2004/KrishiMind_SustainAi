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
            Unified Analyzer
          </p>
          <h1 className="mt-4 text-4xl tracking-tight md:text-5xl">
            Run crop planning and plant disease detection in one workflow.
          </h1>
          <p className="mt-4 text-muted-foreground">
            Add farm context, climate adjustments, and an optional leaf image. The frontend
            sends one request through its server route, then returns crop recommendations
            plus plant disease output from the integrated KrishiMind backend.
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
