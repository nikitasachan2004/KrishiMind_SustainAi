'use client';

import Link from 'next/link';
import React from 'react';
import { Leaf, Menu, X } from 'lucide-react';
import { motion, useScroll } from 'motion/react';
import { usePathname } from 'next/navigation';

import { ThemeToggle } from '@/components/theme/theme-toggle';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const menuItems = [
  { name: 'Home', href: '/' },
  { name: 'Analyzer', href: '/analyze' },
  { name: 'Diseases', href: '/diseases' },
  { name: 'About', href: '/about' },
];

export function SiteHeader() {
  const [menuState, setMenuState] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);
  const pathname = usePathname();
  const { scrollYProgress } = useScroll();

  React.useEffect(() => {
    const unsubscribe = scrollYProgress.on('change', (latest) => {
      setScrolled(latest > 0.04);
    });
    return () => unsubscribe();
  }, [scrollYProgress]);

  React.useEffect(() => {
    setMenuState(false);
  }, [pathname]);

  return (
    <header className="sticky top-0 z-40 px-4 pt-3 sm:px-6 lg:px-8">
      <nav
        data-state={menuState ? 'active' : 'inactive'}
        className={cn(
          'mx-auto max-w-7xl rounded-[1.75rem] border border-border/60 bg-background/80 shadow-sm backdrop-blur-xl transition-all duration-300',
          scrolled && 'shadow-xl shadow-black/5 dark:shadow-black/30'
        )}
      >
        <motion.div
          className={cn(
            'flex flex-wrap items-center justify-between gap-4 px-4 py-3 lg:px-6',
            scrolled && 'py-2.5'
          )}
        >
          <Link href="/" aria-label="KrishiMind SustainAI home" className="flex items-center">
            <Logo />
          </Link>

          <div className="hidden items-center gap-1 lg:flex">
            {menuItems.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'rounded-full px-4 py-2 text-sm font-medium transition',
                    active
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  )}
                >
                  {item.name}
                </Link>
              );
            })}
          </div>

          <div className="hidden items-center gap-3 lg:flex">
            <ThemeToggle />
            <Button asChild className="rounded-full">
              <Link href="/analyze">Open Workspace</Link>
            </Button>
          </div>

          <div className="flex items-center gap-2 lg:hidden">
            <ThemeToggle />
            <button
              type="button"
              onClick={() => setMenuState((value) => !value)}
              aria-label={menuState ? 'Close menu' : 'Open menu'}
              className="rounded-full border border-border/60 bg-background p-2"
            >
              {menuState ? <X className="size-5" /> : <Menu className="size-5" />}
            </button>
          </div>

          <div className="data-[state=inactive]:hidden w-full lg:hidden" data-state={menuState ? 'active' : 'inactive'}>
            <div className="mt-2 rounded-2xl border border-border/60 bg-card p-3">
              <div className="flex flex-col gap-2">
                {menuItems.map((item) => {
                  const active = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        'rounded-xl px-4 py-3 text-sm font-medium transition',
                        active
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                      )}
                    >
                      {item.name}
                    </Link>
                  );
                })}
                <Button asChild className="mt-2 rounded-xl">
                  <Link href="/analyze">Open Analyzer</Link>
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      </nav>
    </header>
  );
}

function Logo() {
  return (
    <div className="flex items-center gap-3 rounded-full border border-primary/20 bg-card/80 px-3 py-2 shadow-sm backdrop-blur">
      <div className="flex size-9 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Leaf className="size-4" />
      </div>
      <div>
        <p className="text-sm font-semibold leading-none">KrishiMind SustainAI</p>
        <p className="text-xs text-muted-foreground">Crop Planning + Plant Health</p>
      </div>
    </div>
  );
}
