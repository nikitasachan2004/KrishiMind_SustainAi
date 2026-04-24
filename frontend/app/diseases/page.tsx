import { Microscope, ScanSearch, Trees } from 'lucide-react';

import { SiteHeader } from '@/components/sections/site-header';
import { SiteFooter } from '@/components/sections/site-footer';

const diseases = [
  'Corn leaf blight',
  'Corn rust leaf',
  'Squash powdery mildew leaf',
  'Peach leaf',
  'Raspberry leaf',
  'Blueberry leaf',
  'Tomato leaf late blight',
  'Potato leaf early blight',
  'Tomato Septoria leaf spot',
  'Tomato leaf bacterial spot',
];

const sampleCards = [
  {
    title: 'Leaf lesion tracking',
    image:
      'https://images.unsplash.com/photo-1512428813834-c702c7702b78?auto=format&fit=crop&w=1200&q=80',
  },
  {
    title: 'Field crop observations',
    image:
      'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1200&q=80',
  },
  {
    title: 'Greenhouse inspection',
    image:
      'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=1200&q=80',
  },
];

export default function DiseasesPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-12">
        <div className="grid gap-12 lg:grid-cols-[0.95fr_1.05fr]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary">
              Disease Library
            </p>
            <h1 className="mt-4 text-4xl tracking-tight md:text-5xl">
              Supported classes alongside the broader KrishiMind planning workflow.
            </h1>
            <p className="mt-4 max-w-xl text-muted-foreground">
              The disease signal is optional in the analyzer, but when a leaf image is provided
              it becomes part of the same advisory flow as crop ranking and climate scenario review.
            </p>
            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              {[
                { icon: ScanSearch, label: 'Rapid screening' },
                { icon: Microscope, label: 'Disease confidence' },
                { icon: Trees, label: 'Crop awareness' },
              ].map((item) => (
                <div key={item.label} className="rounded-[1.5rem] border border-border/60 bg-white/80 p-4">
                  <item.icon className="size-5 text-primary" />
                  <p className="mt-3 text-sm font-medium">{item.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {diseases.map((item) => (
              <div key={item} className="rounded-[1.5rem] border border-border/60 bg-white/90 p-5 shadow-lg shadow-lime-900/5">
                <p className="text-sm text-muted-foreground">Disease class</p>
                <p className="mt-2 text-lg font-semibold">{item}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {sampleCards.map((card) => (
            <article key={card.title} className="overflow-hidden rounded-[2rem] border border-border/60 bg-white/90 shadow-xl shadow-lime-900/5">
              <img src={card.image} alt={card.title} className="h-72 w-full object-cover" />
              <div className="p-6">
                <h2 className="text-2xl">{card.title}</h2>
              </div>
            </article>
          ))}
        </div>
      </section>
      <SiteFooter />
    </div>
  );
}
