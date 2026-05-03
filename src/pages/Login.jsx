import { motion } from "framer-motion";
import { ArrowRight, LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Badge } from "../components/Layout";
import { Button, Card, Input } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

function validateForm({ email, password }) {
  return {
    email: email.trim() ? "" : "Email is required.",
    password: password ? "" : "Password is required.",
  };
}

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, login } = useAuth();
  const { pushToast } = useToast();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const successMessage = location.state?.message || "";

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (successMessage) {
      pushToast({
        title: "Account ready",
        message: successMessage,
        tone: "success",
      });
    }
  }, [pushToast, successMessage]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: "" }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const nextErrors = validateForm(formData);
    setErrors(nextErrors);

    if (nextErrors.email || nextErrors.password) {
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      await login({
        email: formData.email.trim(),
        password: formData.password,
      });

      pushToast({
        title: "Welcome back",
        message: "Your workspace is ready.",
        tone: "success",
      });

      const redirectTo = location.state?.from?.pathname || "/dashboard";
      navigate(redirectTo, { replace: true });
    } catch (requestError) {
      const nextMessage = requestError.message || "Unable to log in. Please try again.";
      setError(nextMessage);
      pushToast({
        title: "Login failed",
        message: nextMessage,
        tone: "error",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-xl">
      <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }}>
        <Card className="overflow-hidden p-0">
          <div className="border-b border-slate-200/70 bg-gradient-to-br from-indigo-50 via-white to-emerald-50 px-6 py-6 dark:border-slate-800/80 dark:from-indigo-950/40 dark:via-slate-950/90 dark:to-emerald-950/30 sm:px-8">
            <div className="space-y-4">
              <Badge tone="indigo">Welcome back</Badge>
              <div>
                <h1 className="font-display text-4xl font-semibold tracking-tight text-slate-950 dark:text-white">
                  Log in to your skill network
                </h1>
                <p className="mt-3 max-w-lg text-sm leading-7 text-slate-600 dark:text-slate-400">
                  Jump back into your matches, live conversations, and profile momentum without losing context.
                </p>
              </div>
            </div>
          </div>

          <div className="grid gap-8 px-6 py-6 sm:px-8 lg:grid-cols-[1fr_0.78fr]">
            <form className="space-y-5" onSubmit={handleSubmit}>
              <Input
                label="Email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                autoComplete="email"
                icon={Mail}
                error={errors.email}
                required
              />
              <Input
                label="Password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                autoComplete="current-password"
                icon={LockKeyhole}
                error={errors.password}
                required
              />

              <div className="flex items-center justify-between text-sm">
                <div className="inline-flex items-center gap-2 text-slate-500 dark:text-slate-400">
                  <ShieldCheck className="h-4 w-4 text-emerald-500" />
                  Secure JWT session
                </div>
                <span className="font-medium text-slate-400">Recovery flow coming soon</span>
              </div>

              {error ? <p className="text-sm font-medium text-rose-500">{error}</p> : null}

              <Button className="w-full py-4 text-base" type="submit" isLoading={isSubmitting} icon={ArrowRight}>
                {isSubmitting ? "Signing in" : "Log in to SkillBarter"}
              </Button>

              <p className="text-sm text-slate-600 dark:text-slate-400">
                New here?{" "}
                <Link to="/register" className="font-semibold text-slate-950 dark:text-white">
                  Create an account
                </Link>
              </p>
            </form>

            <div className="space-y-4 rounded-[1.75rem] bg-slate-950 px-5 py-5 text-white dark:bg-slate-900">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-white/50">Inside your workspace</p>
              <div className="space-y-4">
                {[
                  "Realtime chat with accepted barter partners",
                  "AI-ranked recommendations tuned to your goals",
                  "Professional profile and availability signals",
                ].map((item) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-white/6 px-4 py-3 text-sm text-white/80">
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
