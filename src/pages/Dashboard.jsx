import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Badge, SectionHeading } from "../components/Layout";
import { Button, Card, Stat } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { dashboardStats, featuredSwaps, upcomingSessions } from "../data";

export default function DashboardPage() {
  const navigate = useNavigate();
  const { logout, refreshCurrentUser, user } = useAuth();
  const [profile, setProfile] = useState(user);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const loadUser = async () => {
      try {
        const currentUser = await refreshCurrentUser();
        if (isMounted) {
          setProfile(currentUser);
        }
      } catch (requestError) {
        if (isMounted) {
          setError(requestError.message || "Unable to load your profile.");
          logout();
          navigate("/login", { replace: true });
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
  }, [logout, navigate, refreshCurrentUser]);

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="overflow-hidden bg-ink text-white">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-5">
              <Badge tone="gold">
                {isLoading ? "Loading your account..." : `Good afternoon, ${profile?.name || "Member"}`}
              </Badge>
              <div>
                <h1 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">
                  Your barter network is gaining momentum.
                </h1>
                <p className="mt-4 max-w-2xl text-base leading-7 text-white/70">
                  {isLoading
                    ? "Fetching your account details and barter activity."
                    : `Signed in as ${profile?.email}. You have new requests from people who match your goals.`}
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Button variant="secondary">Update profile</Button>
              <Button as="link" to="/matches" className="bg-white text-ink hover:bg-slate-100">
                Find new matches
              </Button>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-peach to-white">
          {error ? (
            <>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-rose-500">
                Session issue
              </p>
              <p className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink">
                Please sign in again
              </p>
              <p className="mt-3 max-w-sm leading-7 text-slate-600">{error}</p>
            </>
          ) : (
            <>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                Match health
              </p>
              <p className="mt-4 font-display text-6xl font-semibold tracking-tight text-ink">94%</p>
              <p className="mt-3 max-w-sm leading-7 text-slate-600">
                Your profile is outperforming similar members because your availability and learning
                goals are both clear.
              </p>
            </>
          )}
        </Card>
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        {dashboardStats.map((stat) => (
          <Stat key={stat.label} {...stat} />
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <Card className="space-y-6">
          <SectionHeading
            eyebrow="Upcoming"
            title="Your next sessions"
            body="Keep your learning flywheel moving with short, high-value swaps already on the calendar."
          />
          <div className="space-y-4">
            {upcomingSessions.map((session) => (
              <div
                key={session.title}
                className={`rounded-[1.5rem] border border-slate-100 bg-gradient-to-r ${session.tone} p-5`}
              >
                <p className="font-semibold text-ink">{session.title}</p>
                <p className="mt-1 text-sm text-slate-500">{session.time}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="space-y-6">
          <SectionHeading
            eyebrow="Requests"
            title="People ready to trade"
            body="Strong-fit members who align with your current goals and recent activity."
          />
          <div className="space-y-4">
            {featuredSwaps.map((swap) => (
              <div key={swap.name} className="rounded-[1.5rem] border border-slate-100 p-5">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-semibold text-ink">{swap.name}</p>
                    <p className="mt-1 text-sm text-slate-500">Offers {swap.offer}</p>
                    <p className="text-sm text-slate-500">Wants {swap.wants}</p>
                  </div>
                  <div className="flex gap-3">
                    <Button variant="secondary">Pass</Button>
                    <Button>Accept</Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </div>
  );
}
