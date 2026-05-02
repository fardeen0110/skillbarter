import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useRealtime } from "../context/RealtimeContext";

function Logo() {
  return (
    <Link to="/" className="flex items-center gap-3">
      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-ink text-lg font-bold text-white shadow-glow">
        SB
      </div>
      <div>
        <p className="font-display text-lg font-semibold text-ink">SkillBarter</p>
        <p className="text-xs text-slate-500">Trade talent. Grow together.</p>
      </div>
    </Link>
  );
}

export function SectionHeading({ eyebrow, title, body }) {
  return (
    <div className="space-y-3">
      <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">{eyebrow}</p>
      <h2 className="font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
        {title}
      </h2>
      {body ? <p className="max-w-2xl text-base leading-7 text-slate-600">{body}</p> : null}
    </div>
  );
}

export function Badge({ children, tone = "default" }) {
  const tones = {
    default: "bg-white/80 text-slate-700",
    coral: "bg-rose-100 text-rose-700",
    sky: "bg-sky-100 text-sky-700",
    mint: "bg-emerald-100 text-emerald-700",
    gold: "bg-amber-100 text-amber-700",
  };

  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${tones[tone]}`}>
      {children}
    </span>
  );
}

export function AppShell() {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const { unreadCount } = useRealtime();
  const initials =
    user?.name
      ?.split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "SB";

  const navLinkStyles = ({ isActive }) =>
    `rounded-full px-4 py-2 text-sm font-semibold transition ${
      isActive ? "bg-ink text-white" : "text-slate-600 hover:bg-white hover:text-ink"
    }`;

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-mesh bg-[#f7f7f2] text-slate-900">
      <header className="sticky top-0 z-30 border-b border-white/60 bg-[#f7f7f2]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <Logo />
          <nav className="hidden items-center gap-2 rounded-full border border-white/70 bg-white/70 p-1 shadow-sm md:flex">
            <NavLink to="/dashboard" className={navLinkStyles}>
              Dashboard
            </NavLink>
            <NavLink to="/matches" className={navLinkStyles}>
              Matches
            </NavLink>
            <NavLink to="/chat" className={navLinkStyles}>
              Chat
            </NavLink>
          </nav>
          <div className="hidden items-center gap-3 md:flex">
            {unreadCount ? <Badge tone="coral">{unreadCount} alerts</Badge> : null}
            <Badge tone="mint">{user?.email || "Signed in"}</Badge>
            <button
              type="button"
              onClick={handleLogout}
              className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-coral to-gold text-sm font-bold text-white"
              aria-label="Log out"
              title="Log out"
            >
              {initials}
            </button>
          </div>
          <div className="md:hidden">
            <Badge tone="sky">Menu</Badge>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}

export function AuthShell() {
  return (
    <div className="min-h-screen bg-mesh bg-[#f8f4ee]">
      <div className="mx-auto grid min-h-screen max-w-7xl lg:grid-cols-[1.1fr_0.9fr]">
        <section className="relative hidden overflow-hidden px-10 py-12 lg:flex lg:flex-col lg:justify-between">
          <Logo />
          <div className="space-y-8 pb-12">
            <Badge tone="gold">Curated skill economy</Badge>
            <h1 className="max-w-xl font-display text-6xl font-semibold leading-[1.05] tracking-tight text-ink">
              Learn faster by trading what you already know.
            </h1>
            <p className="max-w-lg text-lg leading-8 text-slate-600">
              Discover people who complement your strengths, exchange focused sessions, and build
              momentum with every match.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-[2rem] border border-white/70 bg-white/80 p-6 shadow-glow">
              <p className="text-sm text-slate-500">Avg. match quality</p>
              <p className="mt-3 font-display text-4xl font-semibold text-ink">92%</p>
            </div>
            <div className="rounded-[2rem] border border-white/70 bg-ink p-6 text-white shadow-glow">
              <p className="text-sm text-white/70">Skill swaps this month</p>
              <p className="mt-3 font-display text-4xl font-semibold">1.8k</p>
            </div>
          </div>
        </section>
        <section className="flex items-center px-4 py-10 sm:px-6 lg:px-10">
          <Outlet />
        </section>
      </div>
    </div>
  );
}
