'use client';

import { useMemo, useState } from 'react';
import { Microscope, ScanSearch, Search, Trees } from 'lucide-react';

import { SiteHeader } from '@/components/sections/site-header';
import { SiteFooter } from '@/components/sections/site-footer';
import { cn } from '@/lib/utils';

const diseases = [
  { name: 'Corn (Maize) Cercospora Leaf Spot', category: 'Corn' },
  { name: 'Corn (Maize) Common Rust', category: 'Corn' },
  { name: 'Corn (Maize) Northern Leaf Blight', category: 'Corn' },
  { name: 'Corn (Maize) Healthy Leaf', category: 'Corn' },
  { name: 'Tomato Bacterial Spot', category: 'Tomato' },
  { name: 'Tomato Early Blight', category: 'Tomato' },
  { name: 'Tomato Late Blight', category: 'Tomato' },
  { name: 'Tomato Leaf Mold', category: 'Tomato' },
  { name: 'Tomato Septoria Leaf Spot', category: 'Tomato' },
  { name: 'Tomato Spider Mites (Two-Spotted)', category: 'Tomato' },
  { name: 'Tomato Target Spot', category: 'Tomato' },
  { name: 'Tomato Yellow Leaf Curl Virus', category: 'Tomato' },
  { name: 'Tomato Mosaic Virus', category: 'Tomato' },
  { name: 'Tomato Healthy Leaf', category: 'Tomato' },
  { name: 'Potato Early Blight', category: 'Potato' },
  { name: 'Potato Late Blight', category: 'Potato' },
  { name: 'Potato Healthy Leaf', category: 'Potato' },
  { name: 'Squash Powdery Mildew', category: 'Squash' },
  { name: 'Peach Bacterial Spot', category: 'Orchard' },
  { name: 'Peach Healthy Leaf', category: 'Orchard' },
  { name: 'Raspberry Healthy Leaf', category: 'Orchard' },
  { name: 'Blueberry Healthy Leaf', category: 'Orchard' },
  { name: 'Soybean Healthy Leaf', category: 'Field' },
  { name: 'Pepper Bell Bacterial Spot', category: 'Pepper' },
  { name: 'Pepper Bell Healthy Leaf', category: 'Pepper' },
  { name: 'Apple Scab', category: 'Orchard' },
  { name: 'Apple Black Rot', category: 'Orchard' },
  { name: 'Apple Cedar Rust', category: 'Orchard' },
];

const categories = ['All', 'Corn', 'Tomato', 'Potato', 'Squash', 'Orchard', 'Pepper'];

const sampleCards = [
  {
    title: 'Foliar Lesion Telemetry',
    image:
      'https://images.unsplash.com/photo-1512428813834-c702c7702b78?auto=format&fit=crop&w=1200&q=80',
  },
  {
    title: 'Field Crop Monitoring',
    image:
      'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1200&q=80',
  },
  {
    title: 'Greenhouse Validation',
    image:
      'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=1200&q=80',
  },
];

export default function DiseasesPage() {
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const filteredDiseases = useMemo(() => {
    return diseases.filter((item) => {
      const matchesCat = selectedCategory === 'All' || item.category === selectedCategory;
      const matchesSearch = item.name.toLowerCase().includes(search.toLowerCase());
      return matchesCat && matchesSearch;
    });
  }, [search, selectedCategory]);

  return (
    <div className="min-h-screen">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-12">
        {/* Under Construction Banner */}
        <div className="mb-10 rounded-[2rem] border border-amber-500/40 bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-amber-500/5 p-6 md:p-8 dark:from-amber-950/30 dark:via-orange-950/20 dark:to-slate-900">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="text-3xl">🚧</span>
              <div>
                <h2 className="text-xl font-bold text-amber-900 dark:text-amber-300">
                  Plant Disease Detection Under Construction
                </h2>
                <p className="mt-1 text-sm text-amber-800/80 dark:text-amber-200/70">
                  The disease classification model is currently undergoing retraining, benchmark recalibration, and infrastructure upgrades.
                </p>
              </div>
            </div>
            <span className="rounded-full border border-amber-500/40 bg-amber-500/20 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-amber-900 dark:text-amber-300">
              Maintenance in Progress
            </span>
          </div>
        </div>

        <div className="grid gap-12 lg:grid-cols-[0.95fr_1.05fr]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary">
              Taxonomy Catalog (Reference)
            </p>
            <h1 className="mt-4 text-4xl font-extrabold tracking-tight text-foreground md:text-5xl">
              28 Target Foliar Disease Classes
            </h1>
            <p className="mt-4 max-w-xl text-base leading-relaxed text-muted-foreground">
              This taxonomy catalog represents the 28 foliar crop conditions targeted for the upcoming model release. Live image diagnosis is temporarily paused during calibration.
            </p>

            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              {[
                { icon: ScanSearch, label: 'Rapid screening' },
                { icon: Microscope, label: 'Disease confidence' },
                { icon: Trees, label: 'Crop awareness' },
              ].map((item) => (
                <div key={item.label} className="rounded-[1.5rem] border border-border/60 bg-card/90 p-4 shadow-sm dark:shadow-black/20">
                  <item.icon className="size-5 text-primary" />
                  <p className="mt-3 text-sm font-semibold text-foreground">{item.label}</p>
                </div>
              ))}
            </div>

            {/* Filter Search Input */}
            <div className="mt-8 space-y-3">
              <div className="relative">
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search diseases (e.g. Blight, Rust, Spot)..."
                  className="w-full rounded-2xl border border-border bg-card/90 px-4 py-3 pl-10 text-sm font-medium outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
                <Search className="pointer-events-none absolute left-3.5 top-3.5 size-4 text-muted-foreground" />
              </div>

              {/* Category Pills */}
              <div className="flex flex-wrap gap-2">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSelectedCategory(cat)}
                    className={cn(
                      'rounded-full border px-3 py-1 text-xs font-medium transition',
                      selectedCategory === cat
                        ? 'border-primary bg-primary text-primary-foreground font-semibold'
                        : 'border-border/60 bg-secondary/40 text-muted-foreground hover:border-primary/40 hover:text-foreground'
                    )}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Disease List Grid */}
          <div className="grid gap-3 sm:grid-cols-2 max-h-[600px] overflow-y-auto pr-2">
            {filteredDiseases.map((item) => (
              <div
                key={item.name}
                className="rounded-2xl border border-border/60 bg-card/90 p-4 shadow-sm transition hover:border-primary/40 dark:shadow-black/20"
              >
                <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-bold text-primary">
                  {item.category}
                </span>
                <p className="mt-2 text-base font-bold text-foreground">{item.name}</p>
              </div>
            ))}
            {filteredDiseases.length === 0 && (
              <div className="col-span-2 rounded-2xl border border-dashed border-border/70 p-8 text-center text-sm text-muted-foreground">
                No matching disease classes found for &quot;{search}&quot;.
              </div>
            )}
          </div>
        </div>

        {/* Gallery Cards */}
        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {sampleCards.map((card) => (
            <article key={card.title} className="overflow-hidden rounded-[2rem] border border-border/60 bg-card/90 shadow-xl shadow-lime-900/5 dark:shadow-black/20">
              <img src={card.image} alt={card.title} className="h-72 w-full object-cover" />
              <div className="p-6">
                <h2 className="text-2xl font-bold text-foreground">{card.title}</h2>
              </div>
            </article>
          ))}
        </div>
      </section>
      <SiteFooter />
    </div>
  );
}
