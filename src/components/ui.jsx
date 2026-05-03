import { motion } from "framer-motion";
import { LoaderCircle } from "lucide-react";
import { Link } from "react-router-dom";

export function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

export function Button({
  children,
  as = "button",
  to,
  className = "",
  variant = "primary",
  icon: Icon,
  isLoading = false,
  ...props
}) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 disabled:cursor-not-allowed disabled:opacity-60";
  const variants = {
    primary:
      "bg-primary text-white shadow-premium hover:-translate-y-0.5 hover:bg-indigo-500 dark:bg-primary dark:hover:bg-indigo-400",
    secondary:
      "border border-slate-200 bg-white/90 text-slate-900 hover:-translate-y-0.5 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-950/80 dark:text-white dark:hover:border-slate-700",
    ghost:
      "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900/70",
    dark: "bg-slate-950 text-white hover:-translate-y-0.5 hover:bg-slate-800 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100",
    accent:
      "bg-accent text-white shadow-premium hover:-translate-y-0.5 hover:bg-emerald-500",
    soft:
      "bg-indigo-50 text-primary hover:-translate-y-0.5 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:text-indigo-200 dark:hover:bg-indigo-950",
  };

  const styles = cn(base, variants[variant], className);

  const content = (
    <>
      {isLoading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : Icon ? <Icon className="h-4 w-4" /> : null}
      <span>{children}</span>
    </>
  );

  if (as === "link") {
    return (
      <Link to={to} className={styles} {...props}>
        {content}
      </Link>
    );
  }

  return (
    <button className={styles} {...props}>
      {content}
    </button>
  );
}

export function Card({ children, className = "" }) {
  return (
    <div
      className={cn(
        "relative rounded-[2rem] border border-slate-200/70 bg-white/88 p-6 shadow-premium backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-950/72",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function Input({ label, helper, error, icon: Icon, className = "", inputClassName = "", ...props }) {
  return (
    <label className={cn("block space-y-2", className)}>
      {label ? <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{label}</span> : null}
      <span className="relative block">
        {Icon ? (
          <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400 dark:text-slate-500">
            <Icon className="h-4 w-4" />
          </span>
        ) : null}
        <input
          className={cn(
            "w-full rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-primary/40 focus:ring-4 focus:ring-primary/10 dark:border-slate-800 dark:bg-slate-950/80 dark:text-white dark:placeholder:text-slate-500",
            Icon ? "pl-11" : "",
            error ? "border-rose-300 focus:border-rose-400 focus:ring-rose-100 dark:border-rose-900/80" : "",
            inputClassName,
          )}
          {...props}
        />
      </span>
      {error ? <span className="block text-xs font-medium text-rose-500">{error}</span> : null}
      {!error && helper ? <span className="block text-xs text-slate-500 dark:text-slate-400">{helper}</span> : null}
    </label>
  );
}

export function Textarea({ label, helper, error, className = "", ...props }) {
  return (
    <label className={cn("block space-y-2", className)}>
      {label ? <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{label}</span> : null}
      <textarea
        className={cn(
          "min-h-[120px] w-full rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-primary/40 focus:ring-4 focus:ring-primary/10 dark:border-slate-800 dark:bg-slate-950/80 dark:text-white dark:placeholder:text-slate-500",
          error ? "border-rose-300 dark:border-rose-900/80" : "",
        )}
        {...props}
      />
      {error ? <span className="block text-xs font-medium text-rose-500">{error}</span> : null}
      {!error && helper ? <span className="block text-xs text-slate-500 dark:text-slate-400">{helper}</span> : null}
    </label>
  );
}

export function Select({ label, helper, error, className = "", children, ...props }) {
  return (
    <label className={cn("block space-y-2", className)}>
      {label ? <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{label}</span> : null}
      <select
        className={cn(
          "w-full rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-primary/40 focus:ring-4 focus:ring-primary/10 dark:border-slate-800 dark:bg-slate-950/80 dark:text-white",
          error ? "border-rose-300 dark:border-rose-900/80" : "",
        )}
        {...props}
      >
        {children}
      </select>
      {error ? <span className="block text-xs font-medium text-rose-500">{error}</span> : null}
      {!error && helper ? <span className="block text-xs text-slate-500 dark:text-slate-400">{helper}</span> : null}
    </label>
  );
}

export function StatCard({ label, value, delta, icon: Icon, className = "" }) {
  return (
    <Card className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
        {Icon ? (
          <div className="rounded-2xl bg-slate-100 p-2 text-slate-700 dark:bg-slate-900 dark:text-slate-200">
            <Icon className="h-4 w-4" />
          </div>
        ) : null}
      </div>
      <p className="font-display text-4xl font-semibold tracking-tight text-slate-950 dark:text-white">{value}</p>
      {delta ? <p className="text-sm font-medium text-emerald-600 dark:text-emerald-400">{delta}</p> : null}
    </Card>
  );
}

export function Skeleton({ className = "" }) {
  return <div className={cn("animate-pulse rounded-2xl bg-slate-200/80 dark:bg-slate-800/80", className)} />;
}

export function Spinner({ className = "" }) {
  return <LoaderCircle className={cn("h-5 w-5 animate-spin text-primary", className)} />;
}

export function EmptyState({ icon: Icon, title, body, action }) {
  return (
    <Card className="border-dashed border-slate-300/80 bg-white/70 text-center dark:border-slate-800/80 dark:bg-slate-950/55">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mx-auto max-w-md space-y-4">
        {Icon ? (
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-primary dark:bg-indigo-950/50 dark:text-indigo-200">
            <Icon className="h-6 w-6" />
          </div>
        ) : null}
        <div>
          <p className="font-display text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">{title}</p>
          {body ? <p className="mt-2 text-sm leading-7 text-slate-500 dark:text-slate-400">{body}</p> : null}
        </div>
        {action}
      </motion.div>
    </Card>
  );
}
