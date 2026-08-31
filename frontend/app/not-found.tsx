'use client';

import Link from 'next/link';
import { Leaf } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SiteHeader } from '@/components/sections/site-header';
import { SiteFooter } from '@/components/sections/site-footer';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col justify-between">
      <SiteHeader />
      <main className="mx-auto flex max-w-md flex-col items-center justify-center px-6 py-24 text-center">
        <div className="rounded-full bg-primary/10 p-4 text-primary">
          <Leaf className="size-10" />
        </div>
        <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-foreground">404</h1>
        <p className="mt-2 text-lg font-bold text-foreground">Page Not Found</p>
        <p className="mt-2 text-sm text-muted-foreground">
          The requested route does not exist in the KrishiMind SustainAI portal.
        </p>
        <Button asChild className="mt-8 rounded-full px-6">
          <Link href="/">Return to Home</Link>
        </Button>
      </main>
      <SiteFooter />
    </div>
  );
}
