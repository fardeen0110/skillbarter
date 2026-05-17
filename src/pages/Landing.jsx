import { motion } from "framer-motion";
import {
  ArrowRight,
  MessagesSquare,
  ShieldCheck,
  Sparkles,
  Star,
  Zap,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Badge, Logo, SectionHeading } from "../components/Layout";
import { Button, Card } from "../components/ui";
import {
  featuredSwaps,
  howItWorks,
  landingFeatures,
  testimonials,
  topSkills,
} from "../data";

const fadeInUp = {
  initial: { opacity: 0, y: 18 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.2 },
  transition: { duration: 0.55, ease: "easeOut" },
};

const featureIcons = {
  "Elite match intelligence": Sparkles,
  "Professional social graph": Zap,
  "Realtime barter rooms": MessagesSquare,
};

export default function LandingPage() {
  return (
    <div className="bg-app min-h-screen text-slate-950 dark:text-white">
      <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/60 backdrop-blur-2xl dark:border-slate-800/70 dark:bg-slate-950/55">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <Logo />
          <div className="hidden items-center gap-8 text-sm font-medium text-slate-600 dark:text-slate-300 md:flex">
            <a href="#features" className="transition hover:text-slate-950 dark:hover:text-white">
              Features
            </a>
            <a href="#how-it-works" className="transition hover:text-slate-950 dark:hover:text-white">
              How it works
            </a>
            <a href="#testimonials" className="transition hover:text-slate-950 dark:hover:text-white">
              Testimonials
            </a>
          </div>
          <div className="flex items-center gap-3">
            <Button as="link" to="/login" variant="ghost">
              Log in
            </Button>
            <Button as="link" to="/register">
              Get started
            </Button>
          </div>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 bg-aurora opacity-90" />
          <div className="relative mx-auto grid max-w-7xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:py-24">
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="space-y-8"
            >
              <Badge tone="indigo">Premium skill exchange for ambitious professionals</Badge>
              <div className="space-y-6">
                <h1 className="max-w-3xl font-display text-5xl font-semibold leading-[1.02] tracking-tight sm:text-6xl lg:text-7xl">
                  Trade what you know for what moves your career forward.
                </h1>
                <p className="max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
                  SkillBarter combines AI matchmaking, professional networking, and realtime collaboration into one elite product experience designed to help you learn faster.
                </p>
              </div>

              <div className="flex flex-col gap-4 sm:flex-row">
                <Button as="link" to="/register" className="px-6 py-4 text-base" icon={ArrowRight}>
                  Launch your profile
                </Button>
                <Button as="link" to="/login" variant="secondary" className="px-6 py-4 text-base">
                  Explore the workspace
                </Button>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {[
                  { label: "Match quality", value: "92%" },
                  { label: "Average response", value: "1.7h" },
                  { label: "Repeat swaps", value: "68%" },
                ].map((item) => (
                  <Card key={item.label} className="bg-white/72">
                    <p className="text-sm text-slate-500 dark:text-slate-400">{item.label}</p>
                    <p className="mt-3 font-display text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">
                      {item.value}
                    </p>
                  </Card>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.7 }}
              className="relative"
            >
              <Card className="overflow-hidden bg-slate-950 text-white shadow-float dark:bg-slate-900">
                <div className="absolute inset-0 bg-spotlight opacity-70" />
                <div className="relative space-y-6">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-sm font-semibold uppercase tracking-[0.28em] text-white/60">
                        Today&apos;s best-fit matches
                      </p>
                      <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight">
                        A sharper way to discover who can actually help.
                      </h2>
                    </div>
                    <Badge tone="mint">AI Ranked</Badge>
                  </div>

                  <div className="space-y-4">
                    {featuredSwaps.map((swap) => (
                      <div
                        key={swap.name}
                        className="rounded-[1.75rem] border border-white/10 bg-white/8 px-5 py-4 backdrop-blur-sm"
                      >
                        <div className="flex items-center justify-between gap-4">
                          <div>
                            <p className="font-semibold text-white">{swap.name}</p>
                            <p className="mt-1 text-sm text-white/65">Offers {swap.offer}</p>
                            <p className="text-sm text-white/65">Wants {swap.wants}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-semibold text-emerald-300">{swap.score}</p>
                            <p className="text-xs uppercase tracking-[0.24em] text-white/45">{swap.tag}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="grid gap-4 sm:grid-cols-3">
                    {[
                      { icon: Sparkles, label: "Context-aware ranking" },
                      { icon: MessagesSquare, label: "Realtime social chat" },
                      { icon: ShieldCheck, label: "Professional trust signals" },
                    ].map((item) => {
                      const Icon = item.icon;
                      return (
                        <div key={item.label} className="rounded-[1.5rem] border border-white/10 bg-white/8 p-4">
                          <div className="mb-3 inline-flex rounded-2xl bg-white/10 p-2">
                            <Icon className="h-4 w-4" />
                          </div>
                          <p className="text-sm text-white/75">{item.label}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </Card>
            </motion.div>
          </div>
        </section>

        <section id="features" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <motion.div {...fadeInUp}>
            <SectionHeading
              eyebrow="Why it feels different"
              title="A startup-grade product designed for trust, momentum, and repeat value."
              body="From matchmaking to messaging, every interaction is tuned for professional clarity and low-friction collaboration."
              align="center"
            />
          </motion.div>

          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {landingFeatures.map((feature, index) => {
              const FeatureIcon = featureIcons[feature.title] || Sparkles;

              return (
              <motion.div key={feature.title} {...fadeInUp} transition={{ delay: index * 0.08, duration: 0.55 }}>
                <Card className="h-full">
                  <div className="mb-5 inline-flex rounded-2xl bg-indigo-50 p-3 text-primary dark:bg-indigo-950/60 dark:text-indigo-200">
                    <FeatureIcon className="h-5 w-5" />
                  </div>
                  <h3 className="font-display text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">
                    {feature.title}
                  </h3>
                  <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-400">{feature.body}</p>
                </Card>
              </motion.div>
            );
            })}
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <Card className="overflow-hidden bg-slate-950 text-white dark:bg-slate-900">
            <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr]">
              <div>
                <Badge tone="gold">Skill universe</Badge>
                <h2 className="mt-4 font-display text-4xl font-semibold tracking-tight">
                  A product built for serious professionals, not casual browsing.
                </h2>
                <p className="mt-4 max-w-xl text-base leading-7 text-white/70">
                  Match across design, code, strategy, communication, and emerging AI workflows without the awkwardness of generic networking platforms.
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                {topSkills.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex rounded-full border border-white/10 bg-white/8 px-4 py-2 text-sm text-white/85"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </Card>
        </section>

        <section id="how-it-works" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <motion.div {...fadeInUp}>
            <SectionHeading
              eyebrow="How it works"
              title="A calm, premium flow from profile to first skill swap."
              body="The platform is intentionally simple: signal what you can offer, let the system rank strong-fit introductions, then move into realtime conversation."
            />
          </motion.div>

          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {howItWorks.map((item, index) => (
              <motion.div key={item.step} {...fadeInUp} transition={{ delay: index * 0.08, duration: 0.55 }}>
                <Card className="h-full">
                  <p className="text-sm font-semibold uppercase tracking-[0.26em] text-slate-400">{item.step}</p>
                  <h3 className="mt-4 font-display text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">
                    {item.title}
                  </h3>
                  <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-400">{item.body}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </section>

        <section id="testimonials" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <motion.div {...fadeInUp}>
            <SectionHeading
              eyebrow="Loved by modern builders"
              title="What high-agency members say after their first few exchanges."
              body="The best signal is repeated use. These are the professionals who turned introductions into actual working relationships."
              align="center"
            />
          </motion.div>

          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {testimonials.map((testimonial, index) => (
              <motion.div key={testimonial.name} {...fadeInUp} transition={{ delay: index * 0.08, duration: 0.55 }}>
                <Card className="h-full">
                  <div className="mb-4 flex items-center gap-1 text-amber-400">
                    {Array.from({ length: 5 }).map((_, starIndex) => (
                      <Star key={starIndex} className="h-4 w-4 fill-current" />
                    ))}
                  </div>
                  <p className="text-base leading-8 text-slate-700 dark:text-slate-300">&ldquo;{testimonial.quote}&rdquo;</p>
                  <div className="mt-6">
                    <p className="font-semibold text-slate-950 dark:text-white">{testimonial.name}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{testimonial.role}</p>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 pb-8 sm:px-6 lg:px-8">
          <Card className="overflow-hidden bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-950 text-white shadow-float dark:from-slate-900 dark:via-indigo-950 dark:to-slate-900">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
              <div className="max-w-2xl">
                <Badge tone="mint">Ready to join?</Badge>
                <h2 className="mt-4 font-display text-4xl font-semibold tracking-tight sm:text-5xl">
                  Make your next professional relationship actually useful.
                </h2>
                <p className="mt-4 text-base leading-7 text-white/72">
                  Create your account, define your strengths, and let the platform find the people worth learning with.
                </p>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row">
                <Button as="link" to="/register" variant="accent" className="px-6 py-4">
                  Create free account
                </Button>
                <Button as="link" to="/login" variant="secondary" className="border-white/15 bg-white/10 px-6 py-4 text-white hover:bg-white/15">
                  Log in
                </Button>
              </div>
            </div>
          </Card>
        </section>
      </main>

      <footer className="border-t border-slate-200/70 px-4 py-8 dark:border-slate-800/70 sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 text-sm text-slate-500 dark:text-slate-400 md:flex-row md:items-center md:justify-between">
          <p>SkillBarter. Premium skill exchange for modern professionals.</p>
          <div className="flex items-center gap-5">
            <Link to="/login" className="transition hover:text-slate-950 dark:hover:text-white">
              Log in
            </Link>
            <Link to="/register" className="transition hover:text-slate-950 dark:hover:text-white">
              Register
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
