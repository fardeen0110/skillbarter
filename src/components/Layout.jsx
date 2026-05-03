import { AnimatePresence, motion } from "framer-motion";
import {
  Bell,
  Compass,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquareMore,
  Moon,
  Search,
  Sparkles,
  SunMedium,
  UserCircle2,
  X,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useProfile } from "../context/ProfileContext";
import { useRealtime } from "../context/RealtimeContext";
import { useTheme } from "../context/ThemeContext";
import { Button, Card, cn } from "./ui";

function getInitials(name) {
  return (
    name
      ?.split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "SB"
  );
}

export function Logo({ compact = false }) {
  return (
    <Link to="/" className="flex items-center gap-3">
      <div className="relative flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl bg-slate-950 text-sm font-bold text-white shadow-premium dark:bg-white dark:text-slate-950">
        <span className="absolute inset-0 bg-spotlight opacity-80" />
        <span className="relative">SB</span>
      </div>
      {!compact ? (
        <div>
          <p className="font-display text-lg font-semibold tracking-tight text-slate-950 dark:text-white">
            SkillBarter
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">Trade talent. Build momentum.</p>
        </div>
      ) : null}
    </Link>
  );
}

export function Badge({ children, tone = "default", className = "" }) {
  const tones = {
    default: "bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-200",
    coral: "bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-200",
    sky: "bg-sky-100 text-sky-700 dark:bg-sky-950/60 dark:text-sky-200",
    mint: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-200",
    gold: "bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-200",
    indigo: "bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-200",
  };

  return (
    <span className={cn("inline-flex rounded-full px-3 py-1 text-xs font-semibold", tones[tone], className)}>
      {children}
    </span>
  );
}

export function SectionHeading({ eyebrow, title, body, align = "left" }) {
  return (
    <div className={cn("space-y-3", align === "center" ? "text-center" : "text-left")}>
      {eyebrow ? (
        <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-500 dark:text-slate-400">
          {eyebrow}
        </p>
      ) : null}
      <h2 className="font-display text-3xl font-semibold tracking-tight text-slate-950 dark:text-white sm:text-4xl">
        {title}
      </h2>
      {body ? (
        <p className={cn("text-base leading-7 text-slate-600 dark:text-slate-400", align === "center" ? "mx-auto max-w-2xl" : "max-w-2xl")}>
          {body}
        </p>
      ) : null}
    </div>
  );
}

const navItems = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
  { label: "Matches", to: "/matches", icon: Compass },
  { label: "Chat", to: "/chat", icon: MessageSquareMore },
  { label: "Profile", to: "/profile", icon: UserCircle2 },
];

export function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();
  const { profile } = useProfile();
  const { notifications, unreadCount, markNotificationsRead, connected } = useRealtime();
  const { isDarkMode, toggleTheme } = useTheme();
  const [searchValue, setSearchValue] = useState("");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const initials = getInitials(profile?.name);
  const latestNotifications = useMemo(() => notifications.slice(0, 6), [notifications]);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const toggleNotifications = () => {
    setIsNotificationsOpen((current) => !current);
    setIsProfileOpen(false);
    markNotificationsRead();
  };

  const toggleProfile = () => {
    setIsProfileOpen((current) => !current);
    setIsNotificationsOpen(false);
  };

  const activePage = navItems.find((item) => location.pathname.startsWith(item.to))?.label || "Workspace";

  return (
    <div className="bg-app min-h-screen text-slate-950 dark:text-white">
      <div className="pointer-events-none fixed inset-0 bg-aurora opacity-90 dark:opacity-100" />
      <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/55 backdrop-blur-2xl dark:border-slate-800/70 dark:bg-slate-950/50">
        <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-4 sm:px-6 lg:px-8">
          <Logo />

          <nav className="hidden items-center gap-2 rounded-full border border-slate-200/70 bg-white/75 p-1 shadow-premium dark:border-slate-800/70 dark:bg-slate-950/70 lg:flex">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      "inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition",
                      isActive
                        ? "bg-slate-950 text-white shadow-sm dark:bg-white dark:text-slate-950"
                        : "text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white",
                    )
                  }
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>

          <div className="ml-auto hidden min-w-[260px] flex-1 items-center justify-end gap-3 lg:flex">
            <label className="relative w-full max-w-sm">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-slate-500" />
              <input
                type="text"
                value={searchValue}
                onChange={(event) => setSearchValue(event.target.value)}
                placeholder="Search people, skills, or conversations"
                className="w-full rounded-full border border-slate-200/70 bg-white/78 py-3 pl-11 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-primary/30 focus:ring-4 focus:ring-primary/10 dark:border-slate-800/80 dark:bg-slate-950/72 dark:text-white"
              />
            </label>

            <button
              type="button"
              onClick={toggleNotifications}
              className="relative rounded-2xl border border-slate-200/70 bg-white/78 p-3 text-slate-700 shadow-premium transition hover:-translate-y-0.5 hover:text-slate-950 dark:border-slate-800/80 dark:bg-slate-950/72 dark:text-slate-200 dark:hover:text-white"
              aria-label="Toggle notifications"
            >
              <Bell className="h-4 w-4" />
              {unreadCount ? (
                <span className="absolute -right-1 -top-1 rounded-full bg-rose-500 px-1.5 py-0.5 text-[10px] font-semibold text-white">
                  {unreadCount}
                </span>
              ) : null}
            </button>

            <button
              type="button"
              onClick={toggleTheme}
              className="rounded-2xl border border-slate-200/70 bg-white/78 p-3 text-slate-700 shadow-premium transition hover:-translate-y-0.5 hover:text-slate-950 dark:border-slate-800/80 dark:bg-slate-950/72 dark:text-slate-200 dark:hover:text-white"
              aria-label="Toggle theme"
            >
              {isDarkMode ? <SunMedium className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>

            <button
              type="button"
              onClick={toggleProfile}
              className="flex items-center gap-3 rounded-2xl border border-slate-200/70 bg-white/78 px-3 py-2.5 shadow-premium transition hover:-translate-y-0.5 dark:border-slate-800/80 dark:bg-slate-950/72"
            >
              {profile?.profileImage ? (
                <img src={profile.profileImage} alt={profile.name} className="h-10 w-10 rounded-2xl object-cover" />
              ) : (
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-950 text-sm font-semibold text-white dark:bg-white dark:text-slate-950">
                  {initials}
                </div>
              )}
              <div className="text-left">
                <p className="text-sm font-semibold text-slate-900 dark:text-white">{profile?.name || "Member"}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">{activePage}</p>
              </div>
            </button>
          </div>

          <div className="ml-auto flex items-center gap-2 lg:hidden">
            <button
              type="button"
              onClick={toggleTheme}
              className="rounded-2xl border border-slate-200/70 bg-white/80 p-3 text-slate-700 shadow-premium dark:border-slate-800/80 dark:bg-slate-950/72 dark:text-slate-200"
            >
              {isDarkMode ? <SunMedium className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <button
              type="button"
              onClick={() => setIsMobileMenuOpen((current) => !current)}
              className="rounded-2xl border border-slate-200/70 bg-white/80 p-3 text-slate-700 shadow-premium dark:border-slate-800/80 dark:bg-slate-950/72 dark:text-slate-200"
            >
              {isMobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {isMobileMenuOpen ? (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="border-t border-slate-200/70 px-4 py-4 dark:border-slate-800/70 lg:hidden"
            >
              <div className="mx-auto max-w-7xl space-y-4">
                <label className="relative block">
                  <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-slate-500" />
                  <input
                    type="text"
                    value={searchValue}
                    onChange={(event) => setSearchValue(event.target.value)}
                    placeholder="Search people and skills"
                    className="w-full rounded-2xl border border-slate-200/70 bg-white/80 py-3 pl-11 pr-4 text-sm text-slate-900 outline-none dark:border-slate-800/80 dark:bg-slate-950/72 dark:text-white"
                  />
                </label>
                <div className="grid gap-2 sm:grid-cols-2">
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    return (
                      <NavLink
                        key={item.to}
                        to={item.to}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className={({ isActive }) =>
                          cn(
                            "flex items-center gap-3 rounded-2xl border px-4 py-3 text-sm font-semibold",
                            isActive
                              ? "border-slate-950 bg-slate-950 text-white dark:border-white dark:bg-white dark:text-slate-950"
                              : "border-slate-200/70 bg-white/78 text-slate-700 dark:border-slate-800/80 dark:bg-slate-950/72 dark:text-slate-200",
                          )
                        }
                      >
                        <Icon className="h-4 w-4" />
                        {item.label}
                      </NavLink>
                    );
                  })}
                </div>
                <div className="flex items-center justify-between rounded-2xl border border-slate-200/70 bg-white/78 px-4 py-3 dark:border-slate-800/80 dark:bg-slate-950/72">
                  <div>
                    <p className="text-sm font-semibold text-slate-900 dark:text-white">{profile?.name || "Member"}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{profile?.email}</p>
                  </div>
                  <Button type="button" variant="secondary" onClick={handleLogout} icon={LogOut}>
                    Logout
                  </Button>
                </div>
              </div>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </header>

      <AnimatePresence>
        {isNotificationsOpen ? (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="fixed right-4 top-24 z-50 hidden w-full max-w-sm lg:block"
          >
            <Card className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-900 dark:text-white">Notifications</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {connected ? "Live updates connected" : "Realtime reconnecting"}
                  </p>
                </div>
                <Badge tone={connected ? "mint" : "coral"}>{connected ? "Live" : "Offline"}</Badge>
              </div>
              <div className="space-y-3">
                {latestNotifications.length ? (
                  latestNotifications.map((notification) => (
                    <div
                      key={notification.id}
                      className="rounded-2xl border border-slate-200/70 bg-slate-50/80 px-4 py-3 dark:border-slate-800/80 dark:bg-slate-900/70"
                    >
                      <p className="text-sm font-semibold text-slate-900 dark:text-white">{notification.text}</p>
                      <p className="mt-1 text-xs uppercase tracking-[0.22em] text-slate-400">{notification.type}</p>
                    </div>
                  ))
                ) : (
                  <p className="rounded-2xl bg-slate-50 px-4 py-5 text-sm text-slate-500 dark:bg-slate-900/70 dark:text-slate-400">
                    Nothing urgent right now. New messages and requests will show up here.
                  </p>
                )}
              </div>
            </Card>
          </motion.div>
        ) : null}
      </AnimatePresence>

      <AnimatePresence>
        {isProfileOpen ? (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="fixed right-4 top-24 z-50 hidden w-full max-w-xs lg:block"
          >
            <Card className="space-y-4">
              <div className="flex items-center gap-3">
                {profile?.profileImage ? (
                  <img src={profile.profileImage} alt={profile.name} className="h-14 w-14 rounded-3xl object-cover" />
                ) : (
                  <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-slate-950 text-base font-semibold text-white dark:bg-white dark:text-slate-950">
                    {initials}
                  </div>
                )}
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white">{profile?.name || "Member"}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{profile?.email}</p>
                </div>
              </div>
              <Button as="link" to="/profile" variant="secondary" icon={UserCircle2} onClick={() => setIsProfileOpen(false)}>
                Edit profile
              </Button>
              <Button type="button" variant="ghost" icon={LogOut} className="justify-start" onClick={handleLogout}>
                Log out
              </Button>
            </Card>
          </motion.div>
        ) : null}
      </AnimatePresence>

      <main className="relative z-10 mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}

export function AuthShell() {
  return (
    <div className="bg-app min-h-screen">
      <div className="mx-auto grid min-h-screen max-w-7xl lg:grid-cols-[1.08fr_0.92fr]">
        <section className="relative hidden overflow-hidden px-10 py-12 lg:flex lg:flex-col lg:justify-between">
          <div className="absolute inset-0 bg-aurora opacity-95" />
          <div className="relative">
            <Logo />
          </div>

          <div className="relative space-y-8 pb-12">
            <Badge tone="indigo">Trusted skill exchange for ambitious professionals</Badge>
            <div className="space-y-5">
              <h1 className="max-w-2xl font-display text-6xl font-semibold leading-[1.02] tracking-tight text-slate-950 dark:text-white">
                Build a network where every conversation can teach you something.
              </h1>
              <p className="max-w-xl text-lg leading-8 text-slate-600 dark:text-slate-300">
                SkillBarter helps operators, creators, and builders exchange practical expertise with the polish of a premium SaaS product.
              </p>
            </div>

            <div className="grid max-w-2xl gap-4 md:grid-cols-3">
              {[
                { label: "Avg. match quality", value: "92%" },
                { label: "Swap sessions", value: "18.4k" },
                { label: "Response time", value: "1.7h" },
              ].map((item) => (
                <Card key={item.label} className="bg-white/72">
                  <p className="text-sm text-slate-500">{item.label}</p>
                  <p className="mt-3 font-display text-3xl font-semibold tracking-tight text-slate-950">{item.value}</p>
                </Card>
              ))}
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative flex items-center justify-between rounded-[2rem] border border-white/70 bg-white/70 px-6 py-5 shadow-float"
          >
            <div>
              <p className="text-sm font-semibold text-slate-900">Realtime social graph</p>
              <p className="mt-1 text-sm text-slate-500">Requests, conversations, and discoveries in one calm workspace.</p>
            </div>
            <div className="rounded-2xl bg-slate-950 p-3 text-white">
              <Sparkles className="h-5 w-5" />
            </div>
          </motion.div>
        </section>

        <section className="relative flex items-center px-4 py-10 sm:px-6 lg:px-10">
          <div className="absolute inset-0 bg-[var(--surface-glow)] lg:hidden" />
          <div className="relative w-full">
            <Outlet />
          </div>
        </section>
      </div>
    </div>
  );
}
