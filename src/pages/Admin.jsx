import { Shield, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { SectionHeading } from "../components/Layout";
import { Card, EmptyState, Input, Skeleton, StatCard } from "../components/ui";
import { useProfile } from "../context/ProfileContext";
import { useToast } from "../context/ToastContext";
import { fetchAdminSummary, fetchAdminUsers } from "../services/platform";

export default function AdminPage() {
  const { profile } = useProfile();
  const { pushToast } = useToast();
  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState([]);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!profile?.isAdmin) {
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    Promise.all([fetchAdminSummary(), fetchAdminUsers({ query })])
      .then(([summaryData, usersData]) => {
        if (!isMounted) {
          return;
        }
        setSummary(summaryData);
        setUsers(usersData.items);
      })
      .catch((error) => {
        pushToast({
          title: "Unable to load admin dashboard",
          message: error.message,
          tone: "error",
        });
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [profile?.isAdmin, pushToast, query]);

  if (!profile?.isAdmin) {
    return (
      <EmptyState
        icon={Shield}
        title="Admin access required"
        body="This workspace is available only to administrators with moderation access."
      />
    );
  }

  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="Admin dashboard"
        title="Operational visibility for the live platform"
        body="Monitor user growth, moderation signals, open requests, and messaging volume from one control surface."
      />

      <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-5">
        {isLoading
          ? Array.from({ length: 5 }).map((_, index) => (
              <Card key={index} className="space-y-4">
                <Skeleton className="h-4 w-28" />
                <Skeleton className="h-10 w-20" />
              </Card>
            ))
          : [
              { label: "Total users", value: String(summary.total_users), delta: "Registered accounts" },
              { label: "Verified users", value: String(summary.verified_users), delta: "Trusted identities" },
              { label: "Open requests", value: String(summary.open_learning_requests), delta: "Marketplace demand" },
              { label: "Pending requests", value: String(summary.pending_friend_requests), delta: "Connections awaiting review" },
              { label: "Messages", value: String(summary.total_messages), delta: "Delivered chat volume" },
            ].map((item) => <StatCard key={item.label} {...item} />)}
      </section>

      <section className="space-y-5">
        <Input label="Search users" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by name, email, or city" />
        <div className="grid gap-4">
          {isLoading ? (
            Array.from({ length: 6 }).map((_, index) => (
              <Card key={index} className="space-y-3">
                <Skeleton className="h-4 w-40" />
                <Skeleton className="h-4 w-64" />
              </Card>
            ))
          ) : users.length ? (
            users.map((user) => (
              <Card key={user.id}>
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 dark:bg-slate-900">
                    <Users className="h-5 w-5 text-slate-600 dark:text-slate-300" />
                  </div>
                  <div>
                    <p className="font-semibold text-slate-950 dark:text-white">{user.name}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{user.email}</p>
                    <p className="text-xs uppercase tracking-[0.22em] text-slate-400">{user.city || "No city set"}</p>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <EmptyState icon={Users} title="No users found" body="Try a broader admin search query." />
          )}
        </div>
      </section>
    </div>
  );
}
