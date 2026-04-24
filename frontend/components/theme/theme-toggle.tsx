'use client';

import { Moon, SunMedium } from 'lucide-react';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';

export function ThemeToggle() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const storedTheme = window.localStorage.getItem('plantguard-theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const resolvedTheme =
      storedTheme === 'dark' || storedTheme === 'light'
        ? storedTheme
        : systemPrefersDark
          ? 'dark'
          : 'light';

    document.documentElement.classList.toggle('dark', resolvedTheme === 'dark');
    setTheme(resolvedTheme);
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.classList.toggle('dark', nextTheme === 'dark');
    window.localStorage.setItem('plantguard-theme', nextTheme);
    setTheme(nextTheme);
  };

  return (
    <Button
      type="button"
      variant="outline"
      size="icon"
      onClick={toggleTheme}
      className="rounded-full border-border/60 bg-background/80 backdrop-blur"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? <SunMedium className="size-4" /> : <Moon className="size-4" />}
    </Button>
  );
}
