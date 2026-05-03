import { motion } from "framer-motion";
import { ArrowRight, LockKeyhole, Mail, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Badge } from "../components/Layout";
import { Button, Card, Input } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { registerUser } from "../services/auth";

function validateForm({ firstName, lastName, email, password }) {
  return {
    firstName: firstName.trim() ? "" : "First name is required.",
    lastName: lastName.trim() ? "" : "Last name is required.",
    email: email.trim() ? "" : "Email is required.",
    password: password.length >= 8 ? "" : "Use at least 8 characters.",
  };
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { pushToast } = useToast();
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: "" }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const nextErrors = validateForm(formData);
    setErrors(nextErrors);

    if (Object.values(nextErrors).some(Boolean)) {
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      await registerUser({
        name: `${formData.firstName} ${formData.lastName}`.trim(),
        email: formData.email.trim(),
        password: formData.password,
      });

      pushToast({
        title: "Account created",
        message: "You can log in and start building your network.",
        tone: "success",
      });

      navigate("/login", {
        replace: true,
        state: { message: "Account created successfully. Please log in." },
      });
    } catch (requestError) {
      const nextMessage = requestError.message || "Unable to create your account. Please try again.";
      setError(nextMessage);
      pushToast({
        title: "Registration failed",
        message: nextMessage,
        tone: "error",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-2xl">
      <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }}>
        <Card className="overflow-hidden p-0">
          <div className="border-b border-slate-200/70 bg-gradient-to-br from-emerald-50 via-white to-indigo-50 px-6 py-6 dark:border-slate-800/80 dark:from-emerald-950/30 dark:via-slate-950/90 dark:to-indigo-950/35 sm:px-8">
            <div className="space-y-4">
              <Badge tone="mint">Start for free</Badge>
              <div>
                <h1 className="font-display text-4xl font-semibold tracking-tight text-slate-950 dark:text-white">
                  Create your professional barter profile
                </h1>
                <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600 dark:text-slate-400">
                  Join a high-signal network where people trade practical expertise, not empty connection requests.
                </p>
              </div>
            </div>
          </div>

          <div className="grid gap-8 px-6 py-6 sm:px-8 lg:grid-cols-[1fr_0.74fr]">
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="grid gap-5 sm:grid-cols-2">
                <Input
                  label="First name"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  placeholder="Alex"
                  autoComplete="given-name"
                  icon={UserRound}
                  error={errors.firstName}
                  required
                />
                <Input
                  label="Last name"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  placeholder="Jordan"
                  autoComplete="family-name"
                  icon={UserRound}
                  error={errors.lastName}
                  required
                />
              </div>
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
                placeholder="Choose a secure password"
                helper="At least 8 characters. Your backend JWT flow stays unchanged."
                autoComplete="new-password"
                icon={LockKeyhole}
                error={errors.password}
                required
              />

              {error ? <p className="text-sm font-medium text-rose-500">{error}</p> : null}

              <Button className="w-full py-4 text-base" type="submit" isLoading={isSubmitting} icon={ArrowRight}>
                {isSubmitting ? "Creating account" : "Create my account"}
              </Button>

              <p className="text-sm text-slate-600 dark:text-slate-400">
                Already a member?{" "}
                <Link to="/login" className="font-semibold text-slate-950 dark:text-white">
                  Log in
                </Link>
              </p>
            </form>

            <div className="space-y-4 rounded-[1.75rem] bg-slate-950 px-5 py-5 text-white dark:bg-slate-900">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-white/50">What you unlock</p>
              <div className="space-y-3">
                {[
                  "AI matchmaking powered by skill compatibility and availability overlap",
                  "Startup-quality profile, request, and conversation flows",
                  "A social layer designed for repeat learning, not passive browsing",
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
