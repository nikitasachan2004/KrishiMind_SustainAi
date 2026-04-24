import Link from 'next/link';

const footerLinks = [
  { href: '/', label: 'Home' },
  { href: '/analyze', label: 'Analyze' },
  { href: '/diseases', label: 'Disease Library' },
  { href: '/about', label: 'About' },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-border/60 bg-white/70">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-10 lg:flex-row lg:items-end lg:justify-between lg:px-12">
        <div className="max-w-xl">
          <p className="text-lg font-semibold">KrishiMind SustainAI</p>
          <p className="mt-2 text-sm text-muted-foreground">
            A unified frontend for district-level crop planning, climate scenario analysis,
            and optional plant disease detection powered by the integrated KrishiMind backend.
          </p>
        </div>
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          {footerLinks.map((link) => (
            <Link key={link.href} href={link.href} className="transition hover:text-foreground">
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </footer>
  );
}
