import { Link } from "react-router-dom";
import { Badge, SectionHeading } from "../components/Layout";
import { Button, Card } from "../components/ui";
import { featuredSwaps, topSkills } from "../data";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-mesh bg-[#f6f4ef] text-slate-900">
      <header className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between rounded-full border border-white/70 bg-white/70 px-4 py-3 shadow-sm">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-ink font-bold text-white">
              SB
            </div>
            <div>
              <p className="font-display text-lg font-semibold text-ink">SkillBarter</p>
              <p className="text-xs text-slate-500">Skill exchange, reimagined</p>
            </div>
          </Link>
          <div className="hidden items-center gap-2 md:flex">
            <Button as="link" to="/login" variant="ghost">
              Log in
            </Button>
            <Button as="link" to="/register">
              Start swapping
            </Button>
          </div>
        </div>
      </header>

      <main>
        <section className="mx-auto grid max-w-7xl gap-10 px-4 pb-16 pt-8 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:pb-24 lg:pt-12">
          <div className="space-y-8">
            <Badge tone="coral">Built for curious builders and creative operators</Badge>
            <div className="space-y-6">
              <h1 className="max-w-3xl font-display text-5xl font-semibold leading-[0.98] tracking-tight text-ink sm:text-6xl lg:text-7xl">
                Turn your existing expertise into your next unfair advantage.
              </h1>
              <p className="max-w-xl text-lg leading-8 text-slate-600">
                SkillBarter matches ambitious people who want to trade focused sessions instead of
                paying for another generic course.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Button as="link" to="/register" className="px-7 py-4 text-base">
                Create free account
              </Button>
              <Button as="link" to="/dashboard" variant="secondary" className="px-7 py-4 text-base">
                Preview dashboard
              </Button>
            </div>
            <div className="flex flex-wrap gap-3">
              {topSkills.map((skill) => (
                <Badge key={skill}>{skill}</Badge>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-x-10 top-6 -z-10 h-72 rounded-full bg-gradient-to-r from-sky-200 via-amber-100 to-rose-200 blur-3xl" />
            <Card className="space-y-6 bg-white/90">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">Today’s best-fit matches</p>
                  <p className="font-display text-3xl font-semibold text-ink">3 curated intros</p>
                </div>
                <Badge tone="sky">Live matching</Badge>
              </div>
              <div className="space-y-4">
                {featuredSwaps.map((swap) => (
                  <div
                    key={swap.name}
                    className="rounded-[1.5rem] border border-slate-100 bg-gradient-to-r from-white to-slate-50 p-5"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-semibold text-ink">{swap.name}</p>
                        <p className="mt-2 text-sm text-slate-500">Offers: {swap.offer}</p>
                        <p className="text-sm text-slate-500">Looking for: {swap.wants}</p>
                      </div>
                      <Badge tone="mint">{swap.tag}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <SectionHeading
            eyebrow="How It Works"
            title="A smarter exchange than courses, cold outreach, or random communities."
            body="Create your profile, declare what you can teach and what you want to learn, then let SkillBarter suggest people worth meeting."
          />
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {[
              ["Build your signal", "Showcase the skills you can confidently offer and the goals you care about next."],
              ["Get matched fast", "Our discovery feed surfaces complementary talent and availability that actually lines up."],
              ["Trade focused sessions", "Book practical 1:1 skill swaps and track outcomes so each exchange compounds."],
            ].map(([title, body], index) => (
              <Card key={title} className={index === 1 ? "bg-ink text-white" : ""}>
                <p className={`text-sm ${index === 1 ? "text-white/70" : "text-slate-500"}`}>
                  0{index + 1}
                </p>
                <h3 className="mt-4 font-display text-2xl font-semibold">{title}</h3>
                <p className={`mt-3 leading-7 ${index === 1 ? "text-white/80" : "text-slate-600"}`}>
                  {body}
                </p>
              </Card>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
