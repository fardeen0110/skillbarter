import { motion } from "framer-motion";
import { ArrowRight, LockKeyhole, Mail, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Badge } from "../components/Layout";
import { Button, Card, Input } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { getOAuthStartUrl, registerUser } from "../services/auth";

function GoogleIcon(props) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" {...props}>
      <path
        fill="#4285F4"
        d="M21.81 12.23c0-.71-.06-1.24-.2-1.79H12.2v3.37h5.52c-.11.84-.7 2.11-2 2.96l-.02.11 2.76 2.09.19.02c1.73-1.56 2.73-3.85 2.73-6.76Z"
      />
      <path
        fill="#34A853"
        d="M12.2 21.9c2.7 0 4.96-.87 6.62-2.37l-3.16-2.22c-.85.58-2 .98-3.46.98-2.64 0-4.89-1.72-5.69-4.09l-.11.01-2.87 2.17-.04.1c1.64 3.17 5 5.42 8.71 5.42Z"
      />
      <path
        fill="#FBBC05"
        d="M6.51 14.2a5.95 5.95 0 0 1-.33-1.97c0-.69.12-1.36.32-1.97l-.01-.13-2.91-2.2-.1.04A9.53 9.53 0 0 0 2.46 12c0 1.46.35 2.84.99 4.03l3.06-1.83Z"
      />
      <path
        fill="#EA4335"
        d="M12.2 5.71c1.84 0 3.08.78 3.79 1.43l2.77-2.64C17.15 3.05 14.89 2.1 12.2 2.1c-3.71 0-7.07 2.25-8.71 5.42l3.02 2.29c.82-2.37 3.07-4.1 5.69-4.1Z"
      />
    </svg>
  );
}

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
  const [isGoogleSubmitting, setIsGoogleSubmitting] = useState(false);

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

  const handleGoogleSignup = () => {
    setIsGoogleSubmitting(true);
    window.location.assign(getOAuthStartUrl("google", "/dashboard"));
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

              <div className="relative py-1">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-slate-200 dark:border-slate-800" />
                </div>
                <div className="relative flex justify-center">
                  <span className="bg-white px-3 text-xs font-semibold uppercase tracking-[0.24em] text-slate-400 dark:bg-slate-950 dark:text-slate-500">
                    Or continue with
                  </span>
                </div>
              </div>

              <Button
                className="w-full py-4 text-base"
                type="button"
                variant="secondary"
                isLoading={isGoogleSubmitting}
                icon={GoogleIcon}
                onClick={handleGoogleSignup}
              >
                Continue with Google
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
