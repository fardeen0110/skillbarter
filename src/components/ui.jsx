import { Link } from "react-router-dom";

export function Button({ children, as = "button", to, className = "", variant = "primary", ...props }) {
  const base =
    "inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold transition duration-200 disabled:cursor-not-allowed disabled:opacity-60";
  const variants = {
    primary: "bg-ink text-white hover:-translate-y-0.5 hover:bg-slate-800",
    secondary: "bg-white text-ink ring-1 ring-slate-200 hover:-translate-y-0.5 hover:ring-slate-300",
    ghost: "text-slate-700 hover:bg-white/80",
  };

  const styles = `${base} ${variants[variant]} ${className}`.trim();

  if (as === "link") {
    return (
      <Link to={to} className={styles} {...props}>
        {children}
      </Link>
    );
  }

  return (
    <button className={styles} {...props}>
      {children}
    </button>
  );
}

export function Card({ children, className = "" }) {
  return (
    <div className={`rounded-[2rem] border border-white/70 bg-white/80 p-6 shadow-glow ${className}`}>
      {children}
    </div>
  );
}

export function Input({ label, helper, ...props }) {
  return (
    <label className="block space-y-2">
      <span className="text-sm font-semibold text-slate-700">{label}</span>
      <input
        className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
        {...props}
      />
      {helper ? <span className="block text-xs text-slate-500">{helper}</span> : null}
    </label>
  );
}

export function Stat({ label, value, delta }) {
  return (
    <Card className="space-y-3">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="font-display text-4xl font-semibold tracking-tight text-ink">{value}</p>
      <p className="text-sm font-medium text-emerald-600">{delta}</p>
    </Card>
  );
}
