'use client';

import Link from 'next/link';
import { ChevronRight, Leaf } from 'lucide-react';

import { SiteHeader } from '@/components/sections/site-header';
import { Button } from '@/components/ui/button';
import { InfiniteSlider } from '@/components/ui/infinite-slider';
import { ProgressiveBlur } from '@/components/ui/progressive-blur';

export function HeroSection() {
  return (
    <>
      <SiteHeader />
      <main className="overflow-x-hidden">
        <section>
          <div className="relative py-20 md:pb-28 lg:pb-32 lg:pt-28">
            <div className="relative z-10 mx-auto flex max-w-7xl flex-col px-6 lg:block lg:px-12">
              <div className="mx-auto max-w-lg text-center lg:ml-0 lg:max-w-full lg:text-left">
                <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-white/70 px-4 py-2 text-sm text-muted-foreground shadow-sm backdrop-blur dark:bg-slate-900/70">
                  <Leaf className="size-4 text-primary" />
                  AI-powered diagnosis for farms, labs, and field teams
                </div>
                <h1 className="mt-8 max-w-3xl text-balance text-5xl tracking-tight md:text-6xl lg:mt-16 xl:text-7xl">
                  Detect plant disease before it spreads across the crop.
                </h1>
                <p className="mt-8 max-w-2xl text-balance text-lg text-muted-foreground">
                  Upload a leaf image, get fast model predictions, review confidence
                  scores, and move from inspection to action with a cleaner workflow.
                </p>

                <div className="mt-12 flex flex-col items-center justify-center gap-2 sm:flex-row lg:justify-start">
                  <Button asChild size="lg" className="h-12 rounded-full pl-5 pr-3 text-base">
                    <Link href="/analyze">
                      <span className="text-nowrap">Start Diagnosis</span>
                      <ChevronRight className="ml-1" />
                    </Link>
                  </Button>
                  <Button
                    asChild
                    size="lg"
                    variant="ghost"
                    className="h-12 rounded-full px-5 text-base hover:bg-zinc-950/5 dark:hover:bg-white/5"
                  >
                    <Link href="/diseases">
                      <span className="text-nowrap">Browse Disease Library</span>
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
            <div className="absolute inset-1 overflow-hidden rounded-3xl border border-black/10 bg-gradient-to-br from-lime-100 via-white to-emerald-100 dark:border-white/10 dark:from-slate-950 dark:via-slate-900 dark:to-emerald-950 sm:aspect-video lg:rounded-[3rem]">
              <video
                autoPlay
                loop
                muted
                playsInline
                className="size-full object-cover opacity-35 mix-blend-multiply dark:opacity-25"
                src="https://ik.imagekit.io/lrigu76hy/tailark/dna-video.mp4?updatedAt=1745736251477"
              />
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.65),transparent_45%)] dark:bg-[radial-gradient(circle_at_top,rgba(120,255,170,0.12),transparent_35%)]" />
            </div>
          </div>
        </section>
        <section className="bg-background pb-2">
          <div className="group relative m-auto max-w-7xl px-6">
            <div className="flex flex-col items-center md:flex-row">
              <div className="md:max-w-44 md:border-r md:pr-6">
                <p className="text-end text-sm text-muted-foreground">
                  Built for precision agriculture and smart crop monitoring
                </p>
              </div>
              <div className="relative py-6 md:w-[calc(100%-11rem)]">
                <InfiniteSlider duration={38} durationOnHover={60} gap={112}>
                  {['FastAPI', 'PyTorch', 'Next.js', 'Tailwind', 'TensorBoard', 'MPS GPU', 'EfficientNet', 'Streamlit'].map(
                    (item) => (
                      <div
                        key={item}
                        className="flex rounded-full border border-border/60 bg-white/80 px-5 py-2 text-sm font-medium text-foreground shadow-sm dark:bg-slate-900/80"
                      >
                        {item}
                      </div>
                    )
                  )}
                </InfiniteSlider>

                <div className="bg-gradient-to-r from-background absolute inset-y-0 left-0 w-20" />
                <div className="bg-gradient-to-l from-background absolute inset-y-0 right-0 w-20" />
                <ProgressiveBlur
                  className="pointer-events-none absolute left-0 top-0 h-full w-20"
                  direction="left"
                  blurIntensity={1}
                />
                <ProgressiveBlur
                  className="pointer-events-none absolute right-0 top-0 h-full w-20"
                  direction="right"
                  blurIntensity={1}
                />
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
