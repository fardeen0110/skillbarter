import { createContext, useContext, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Info, TriangleAlert } from "lucide-react";
import { cn } from "../components/ui";

const ToastContext = createContext(null);

const tones = {
  success: {
    icon: CheckCircle2,
    className:
      "border-emerald-200/70 bg-white/95 text-slate-900 dark:border-emerald-900/80 dark:bg-slate-950/95 dark:text-white",
  },
  error: {
    icon: TriangleAlert,
    className:
      "border-rose-200/70 bg-white/95 text-slate-900 dark:border-rose-900/80 dark:bg-slate-950/95 dark:text-white",
  },
  info: {
    icon: Info,
    className:
      "border-indigo-200/70 bg-white/95 text-slate-900 dark:border-indigo-900/80 dark:bg-slate-950/95 dark:text-white",
  },
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const value = useMemo(
    () => ({
      pushToast({ title, message, tone = "info" }) {
        const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        setToasts((current) => [{ id, title, message, tone }, ...current].slice(0, 4));
        window.setTimeout(() => {
          setToasts((current) => current.filter((toast) => toast.id !== id));
        }, 3200);
      },
      dismissToast(id) {
        setToasts((current) => current.filter((toast) => toast.id !== id));
      },
    }),
    [],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed inset-x-4 top-4 z-[80] flex justify-end sm:inset-x-6 lg:right-8 lg:left-auto">
        <div className="flex w-full max-w-sm flex-col gap-3">
          <AnimatePresence>
            {toasts.map((toast) => {
              const tone = tones[toast.tone] || tones.info;
              const Icon = tone.icon;

              return (
                <motion.div
                  key={toast.id}
                  initial={{ opacity: 0, y: -12, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -12, scale: 0.96 }}
                  className={cn(
                    "pointer-events-auto rounded-3xl border px-4 py-4 shadow-float backdrop-blur-xl",
                    tone.className,
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className="rounded-2xl bg-slate-100 p-2 text-slate-700 dark:bg-slate-900 dark:text-slate-200">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold">{toast.title}</p>
                      {toast.message ? <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{toast.message}</p> : null}
                    </div>
                    <button
                      type="button"
                      onClick={() => value.dismissToast(toast.id)}
                      className="text-xs font-semibold text-slate-400 transition hover:text-slate-700 dark:hover:text-slate-200"
                    >
                      Close
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }

  return context;
}
