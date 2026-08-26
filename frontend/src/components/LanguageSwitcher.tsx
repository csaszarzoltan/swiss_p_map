"use client";

import {useLocale} from 'next-intl';
import {usePathname, useRouter} from 'next/navigation';
import {routing} from '@/i18n/routing';

export default function LanguageSwitcher() {
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();

  function switchLocale(next: string) {
    // replace /de/... -> /fr/... (localePrefix always)
    const segs = pathname.split('/');
    if (routing.locales.includes(segs[1] as never)) segs[1] = next;
    else segs.splice(1, 0, next);
    router.push(segs.join('/') || `/${next}`);
  }

  return (
    <div className="flex gap-1 rounded-full border border-white/10 bg-black/30 px-1 py-1 backdrop-blur">
      {routing.locales.map((l) => (
        <button
          key={l}
          onClick={() => switchLocale(l)}
          aria-current={l === locale ? 'true' : undefined}
          className={`rounded-full px-2.5 py-1 text-xs font-semibold transition ${l === locale ? 'bg-white text-slate-900' : 'text-slate-400 hover:text-white'}`}
        >
          {l.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
