import { motion } from "framer-motion";
import {
  ArrowRight,
  BellRing,
  ChartNoAxesCombined,
  Compass,
  Flame,
  Layers3,
  MessageSquareShare,
  Sparkles,
  Trophy,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Badge, SectionHeading } from "../components/Layout";
import { Button, Card, Skeleton, StatCard } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { useProfile } from "../context/ProfileContext";
import { useRealtime } from "../context/RealtimeContext";
import { useToast } from "../context/ToastContext";
import {
  activityFeed,
  dashboardStats,
  featuredSwaps,
  notificationHighlights,
  skillProgress,
  upcomingSessions,
} from "../data";

const dashboardStatsWithIcons = [
  { label: "Active matches", icon: ChartNoAxesCombined },
  { label: "Reply rate", icon: Sparkles },
  { label: "Hours exchanged", icon: Trophy },
  { label: "Trust score", icon: Flame },
];

export default function DashboardPage() {
  const { logout, refreshCurrentUser, user } = useAuth();
  const { profile } = useProfile();
  const { notifications } = useRealtime();
  const { pushToast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [account, setAccount] = useState(user);

  useEffect(() => {
    let isMounted = true;

    const loadUser = async () => {
      try {
        const currentUser = await refreshCurrentUser();
        if (isMounted) {
          setAccount(currentUser);
        }
      } catch (requestError) {
        const nextMessage = requestError.message || "Unable to load your account.";
        if (isMounted) {
          setError(nextMessage);
          pushToast({
            title: "Session expired",
            message: nextMessage,
            tone: "error",
          });
          logout();
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadUser();

    return () => {
      isMounted = false;
    };
  }, [logout, pushToast, refreshCurrentUser]);

  const highlightNotifications = useMemo(() => {
    if (notifications.length) {
      return notifications.slice(0, 3).map((item) => item.text);
    }

    return notificationHighlights;
  }, [notifications]);

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        <Card className="overflow-hidden bg-slate-950 text-white shadow-float dark:bg-slate-900">
          <div className="absolute inset-0 bg-spotlight opacity-70" />
          <div className="relative flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-5">
              <Badge tone="mint">
                {isLoading ? "Loading your workspace" : `Welcome back, ${profile?.name || account?.name || "Member"}`}
              </Badge>
              <div>
                <h1 className="max-w-3xl font-display text-4xl font-semibold tracking-tight sm:text-5xl">
                  Your network is compounding into real learning leverage.
                </h1>
                <p className="mt-4 max-w-2xl text-base leading-7 text-white/70">
                  {isLoading
                    ? "Refreshing your latest account and social activity."
                    : `${profile?.bio || "Your profile is active."} Signed in as ${account?.email}.`}
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <Button as="link" to="/profile" variant="secondary" className="border-white/15 bg-white/10 text-white hover:bg-white/15">
                Edit profile
              </Button>
              <Button as="link" to="/matches" variant="accent" icon={Compass}>
                Find premium matches
              </Button>
            </div>
          </div>
        </Card>

        <Card className="space-y-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
                Workspace pulse
              </p>
              <p className="mt-2 font-display text-5xl font-semibold tracking-tight text-slate-950 dark:text-white">
                94%
              </p>
            </div>
            <div className="rounded-3xl bg-indigo-50 p-3 text-primary dark:bg-indigo-950/60 dark:text-indigo-200">
              <Sparkles className="h-6 w-6" />
            </div>
          </div>
          <p className="text-sm leading-7 text-slate-600 dark:text-slate-400">
            Your profile is outperforming similar members because your skills, availability, and conversation response rate are all clear.
          </p>
          {error ? <p className="text-sm font-medium text-rose-500">{error}</p> : null}
          <div className="grid gap-3 sm:grid-cols-3">
            {[
              { label: "Profile views", value: "128" },
              { label: "New intros", value: "14" },
              { label: "Chat replies", value: "<2h" },
            ].map((item) => (
              <div key={item.label} className="rounded-2xl border border-slate-200/70 bg-slate-50/80 px-4 py-4 dark:border-slate-800/70 dark:bg-slate-900/70">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-400">{item.label}</p>
                <p className="mt-2 text-xl font-semibold text-slate-950 dark:text-white">{item.value}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {dashboardStats.map((stat, index) => {
          const Icon =
            dashboardStatsWithIcons.find((item) => item.label === stat.label)?.icon || ChartNoAxesCombined;
          return (
            <motion.div key={stat.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.06 }}>
              {isLoading ? (
                <Card className="space-y-4">
                  <Skeleton className="h-4 w-28" />
                  <Skeleton className="h-10 w-24" />
                  <Skeleton className="h-4 w-36" />
                </Card>
              ) : (
                <StatCard {...stat} icon={Icon} />
              )}
            </motion.div>
          );
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.95fr]">
        <Card className="space-y-6">
          <SectionHeading
            eyebrow="Recent activity"
            title="Signals that moved your profile forward"
            body="Your recent requests, completions, and discovery momentum are all visible here."
          />
          <div className="space-y-4">
            {activityFeed.map((item) => (
              <div
                key={item.title}
                className="rounded-[1.75rem] border border-slate-200/70 bg-slate-50/75 px-5 py-5 dark:border-slate-800/70 dark:bg-slate-900/70"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-semibold text-slate-950 dark:text-white">{item.title}</p>
                    <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-400">{item.body}</p>
                  </div>
                  <Badge tone="indigo">{item.time}</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="space-y-6">
          <SectionHeading
            eyebrow="Suggested matches"
            title="People worth prioritizing next"
            body="Curated recommendations based on your current profile and active learning goals."
          />
          <div className="space-y-4">
            {featuredSwaps.map((swap) => (
              <div
                key={swap.name}
                className="rounded-[1.75rem] border border-slate-200/70 bg-white/75 px-5 py-5 dark:border-slate-800/70 dark:bg-slate-900/70"
              >
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-semibold text-slate-950 dark:text-white">{swap.name}</p>
                    <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Offers {swap.offer}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Wants {swap.wants}</p>
                  </div>
                  <div className="text-right">
                    <Badge tone="mint">{swap.score}</Badge>
                    <p className="mt-2 text-xs uppercase tracking-[0.22em] text-slate-400">{swap.tag}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <Button as="link" to="/matches" variant="secondary" icon={ArrowRight}>
            Open matchmaking
          </Button>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card className="space-y-6">
          <SectionHeading
            eyebrow="Upcoming sessions"
            title="Your next high-value exchanges"
            body="Keep your calendar full of focused conversations that compound into real capability."
          />
          <div className="space-y-4">
            {upcomingSessions.map((session) => (
              <div
                key={session.title}
                className={`rounded-[1.75rem] border border-slate-200/60 bg-gradient-to-r ${session.tone} px-5 py-5 dark:border-slate-800/70`}
              >
                <p className="font-semibold text-slate-950">{session.title}</p>
                <p className="mt-2 text-sm text-slate-600">{session.time}</p>
              </div>
            ))}
          </div>
        </Card>

        <div className="grid gap-6">
          <Card className="space-y-6">
            <SectionHeading
              eyebrow="Skill positioning"
              title="What your marketable expertise looks like right now"
              body="Use this to understand where your profile feels strongest inside the network."
            />
            <div className="space-y-4">
              {skillProgress.map((item) => (
                <div key={item.label} className="space-y-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold text-slate-900 dark:text-white">{item.label}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{item.value}%</p>
                  </div>
                  <div className="h-3 rounded-full bg-slate-100 dark:bg-slate-900">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
                      style={{ width: `${item.value}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{item.note}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="space-y-5">
            <div className="flex items-center justify-between gap-3">
              <SectionHeading
                eyebrow="Notifications"
                title="What deserves your attention"
                body="Short, high-signal updates from your network and workspace."
              />
              <div className="rounded-2xl bg-slate-100 p-3 text-slate-700 dark:bg-slate-900 dark:text-slate-200">
                <BellRing className="h-4 w-4" />
              </div>
            </div>
            <div className="space-y-3">
              {highlightNotifications.map((item) => (
                <div
                  key={item}
                  className="rounded-2xl border border-slate-200/70 bg-slate-50/75 px-4 py-4 text-sm text-slate-600 dark:border-slate-800/70 dark:bg-slate-900/70 dark:text-slate-300"
                >
                  {item}
                </div>
              ))}
            </div>
            <div className="flex gap-3">
              <Button as="link" to="/chat" variant="secondary" icon={MessageSquareShare}>
                Open chat
              </Button>
              <Button as="link" to="/profile" variant="soft" icon={Layers3}>
                Refine profile
              </Button>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
