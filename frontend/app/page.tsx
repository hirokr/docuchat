import Image from "next/image";
import Link from "next/link";
import {
  BadgeCheck,
  Brain,
  Code,
  Gauge,
  Layers,
  Lock,
  Play,
  Quote,
  Terminal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const HERO_IMAGE =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuBC9UZCdcOV2K1HbeoJkRhZ9_go50N0sVaYDLWn1W71jG-2yQ0XwV2zHireRerP1WcGaSwhaStV-InRr5QOINtS7r0CDPjqJgI4m3mMdeAhDGYg8V6tJBnYXjryNrL90lM-vPWNjq4SULctWWqGDON8GVXpMx0cwCAXtNDn6vt3tcZoD9aUaq6TOHb-uYyTPz5KbaTGgafR5A8IDCee93d14qESP57Xxfy7feZzKC--Lsn88s8DTzFyVrsp3JH9ve8Lpn2M_-SFUMQ";

const FEATURES = [
  {
    index: "01 / FEATURE",
    labelClass: "text-primary",
    title: "Multi-PDF Support",
    description:
      "Aggregate insights across thousands of pages simultaneously. Our engine synthesizes data from multiple sources in real-time.",
    icon: Layers,
    iconClass: "text-secondary",
    hoverBorder: "hover:border-secondary",
    progressClass: "bg-secondary w-2/3 group-hover:w-full",
  },
  {
    index: "02 / FEATURE",
    labelClass: "text-secondary",
    title: "Instant Citations",
    description:
      "No more hallucinations. Every response is pinned to exact page and line coordinates within your source documents.",
    icon: Quote,
    iconClass: "text-primary",
    hoverBorder: "hover:border-primary",
    progressClass: "bg-primary w-1/2 group-hover:w-full",
  },
  {
    index: "03 / FEATURE",
    labelClass: "text-primary",
    title: "Context-Aware AI",
    description:
      "The AI remembers previous interactions and maintains deep context, understanding the nuances of your specific domain.",
    icon: Brain,
    iconClass: "text-secondary",
    hoverBorder: "hover:border-secondary",
    progressClass: "bg-secondary w-3/4 group-hover:w-full",
  },
] as const;

const TRUST_BADGES = [
  { icon: BadgeCheck, label: "High Performance Mode Active" },
  { icon: Lock, label: "Zero-Retention Security" },
  { icon: Gauge, label: "Sub-100ms Response" },
] as const;

function ChatLink({
  children,
  className,
  size = "default",
}: {
  children: React.ReactNode;
  className?: string;
  size?: "default" | "hero";
}) {
  return (
    <Button
      asChild
      variant="secondary"
      size={size === "hero" ? "lg" : "sm"}
      className={cn(
        "font-display font-bold active:scale-95 transition-transform",
        size === "hero" &&
          "h-auto px-xl py-md text-headline-md font-extrabold brutalist-shadow hover:translate-x-1 hover:translate-y-1 hover:shadow-none",
        className
      )}
    >
      <Link href="/chat">{children}</Link>
    </Button>
  );
}

export default function Home() {
  return (
    <>
      <nav className="fixed top-0 left-0 z-50 mx-auto flex w-full max-w-container-max items-center justify-between border-b border-white/10 bg-surface/80 px-md py-sm backdrop-blur-md">
        <div className="flex items-center gap-md">
          <span className="font-display text-headline-md font-bold tracking-tighter text-on-surface">
            DocuChat
          </span>
          <div className="hidden gap-md md:flex">
            {["Labs", "Docs", "Pricing"].map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase()}`}
                className="text-body-md text-on-surface-variant transition-colors hover:text-on-surface"
              >
                {item}
              </a>
            ))}
          </div>
        </div>
        <ChatLink>Go to Chat</ChatLink>
      </nav>

      <main className="relative pt-20">
        <section
          id="labs"
          className="relative flex min-h-[min(921px,100dvh)] flex-col items-center justify-center px-gutter py-xl grid-mesh"
        >
          <div
            className="pointer-events-none absolute top-0 left-1/2 h-full w-full -translate-x-1/2 bg-gradient-to-b from-primary/10 via-transparent to-transparent"
            aria-hidden
          />

          <div className="relative z-10 w-full max-w-5xl text-center">
            <div className="mb-md inline-block border border-secondary/50 bg-secondary/5 px-sm py-xs">
              <span className="font-label text-label-md uppercase tracking-[0.2em] text-secondary">
                The Future of Interaction
              </span>
            </div>

            <h1 className="mb-lg font-display text-[clamp(2rem,8vw,64px)] leading-none font-extrabold tracking-tight">
              CHATTING WITH DOCUMENTS JUST GOT{" "}
              <span className="text-secondary underline decoration-4 underline-offset-8 decoration-secondary/30">
                LOUD
              </span>
            </h1>

            <div className="group relative mx-auto mt-lg aspect-video max-w-4xl overflow-hidden border border-white/10 bg-surface-container-highest brutalist-shadow">
              <Image
                src={HERO_IMAGE}
                alt="Futuristic document workspace with neon green and violet lighting"
                fill
                priority
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 896px"
                className="object-cover opacity-40 transition-transform duration-700 group-hover:scale-105"
              />
              <div className="relative z-20 flex h-full flex-col items-center justify-center gap-md">
                <button
                  type="button"
                  aria-label="Watch the labs preview"
                  className="flex size-20 items-center justify-center bg-secondary glow-border-lime transition-transform active:scale-90 sm:size-24"
                >
                  <Play
                    className="size-10 fill-surface-dim text-surface-dim sm:size-12"
                    aria-hidden
                  />
                </button>
                <span className="font-label text-label-md text-secondary animate-pulse-glow">
                  WATCH THE LABS PREVIEW
                </span>
              </div>
              <div
                className="absolute top-0 left-0 m-sm size-8 border-t-2 border-l-2 border-secondary"
                aria-hidden
              />
              <div
                className="absolute right-0 bottom-0 m-sm size-8 border-r-2 border-b-2 border-secondary"
                aria-hidden
              />
            </div>
          </div>
        </section>

        <section className="relative mx-auto max-w-container-max overflow-hidden px-gutter py-xl">
          <div className="mb-xl flex flex-col items-end justify-between border-b border-white/10 pb-md md:flex-row">
            <div>
              <h2 className="mb-xs font-display text-headline-lg text-secondary">
                THE LAB
              </h2>
              <p className="max-w-xl text-body-lg text-on-surface-variant">
                Experimental AI features pushed to the absolute limit. No
                boundaries, just high-performance document intelligence.
              </p>
            </div>
            <p className="mt-md font-label text-label-sm tracking-widest text-secondary/50 uppercase md:mt-0">
              Version 1.0.4 experimental
            </p>
          </div>

          <div className="grid grid-cols-1 gap-gutter md:grid-cols-3">
            {FEATURES.map((feature) => (
              <article
                key={feature.title}
                className={cn(
                  "group relative border border-white/10 bg-surface-container p-md transition-all duration-300 glass-panel",
                  feature.hoverBorder
                )}
              >
                <div className="absolute -top-4 -right-4 flex size-12 items-center justify-center border border-white/10 bg-surface-container">
                  <feature.icon
                    className={cn("size-6", feature.iconClass)}
                    aria-hidden
                  />
                </div>
                <span
                  className={cn(
                    "mb-sm block font-label text-label-sm",
                    feature.labelClass
                  )}
                >
                  {feature.index}
                </span>
                <h3 className="mb-md font-display text-headline-md">
                  {feature.title}
                </h3>
                <p className="mb-lg text-body-md text-on-surface-variant">
                  {feature.description}
                </p>
                <div className="h-1 w-full bg-surface-variant">
                  <div
                    className={cn(
                      "h-full transition-all duration-1000",
                      feature.progressClass
                    )}
                  />
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="relative px-gutter py-xl text-center">
          <div
            className="pointer-events-none absolute inset-0 -skew-y-3 bg-primary/5"
            aria-hidden
          />
          <div className="relative z-10 mx-auto max-w-3xl">
            <h2 className="mb-lg font-display text-headline-lg">
              READY TO BREAK THE SILENCE?
            </h2>
            <div className="group relative inline-block">
              <div
                className="absolute -inset-4 bg-secondary/20 opacity-0 blur-xl transition-opacity duration-500 group-hover:opacity-100"
                aria-hidden
              />
              <ChatLink size="hero">Go to Chat</ChatLink>
            </div>
            <ul className="mt-xl flex flex-wrap justify-center gap-md">
              {TRUST_BADGES.map(({ icon: Icon, label }) => (
                <li key={label} className="flex items-center gap-xs">
                  <Icon className="size-4 text-secondary" aria-hidden />
                  <span className="font-label text-label-sm opacity-60">
                    {label}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>

      <footer className="mt-xl flex w-full flex-col items-center justify-between gap-md border-t border-white/10 bg-surface-container-lowest px-md py-xl md:flex-row">
        <div className="flex flex-col items-center gap-xs md:items-start">
          <span className="font-display text-headline-md font-bold text-on-surface">
            DocuChat
          </span>
          <span className="font-label text-label-sm text-on-surface-variant opacity-80">
            © 2024 DocuChat AI. Experimental Build v1.0.4
          </span>
        </div>
        <nav className="flex gap-md" aria-label="Footer">
          {["Security", "Privacy", "API", "Changelog"].map((item) => (
            <a
              key={item}
              href="#"
              className="font-label text-label-sm text-on-surface-variant decoration-secondary decoration-2 transition-all hover:text-secondary hover:underline"
            >
              {item}
            </a>
          ))}
        </nav>
        <div className="flex gap-sm">
          {[Terminal, Code].map((Icon, i) => (
            <button
              key={i}
              type="button"
              aria-label={i === 0 ? "Developer terminal" : "Source code"}
              className="flex size-8 cursor-pointer items-center justify-center border border-white/10 opacity-80 transition-colors hover:border-secondary hover:opacity-100"
            >
              <Icon className="size-4 text-on-surface" aria-hidden />
            </button>
          ))}
        </div>
      </footer>
    </>
  );
}
