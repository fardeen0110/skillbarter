import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Badge } from "../components/Layout";
import { Button, Card, Input } from "../components/ui";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, login } = useAuth();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const successMessage = location.state?.message || "";
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
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await login({
        email: formData.email.trim(),
        password: formData.password,
      });
      const redirectTo = location.state?.from?.pathname || "/dashboard";
      navigate(redirectTo, { replace: true });
    } catch (requestError) {
      setError(requestError.message || "Unable to log in. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-lg">
      <Card className="space-y-8 bg-white/90">
        <div className="space-y-4">
          <Badge tone="sky">Welcome back</Badge>
          <div>
            <h1 className="font-display text-4xl font-semibold tracking-tight text-ink">Log in</h1>
            <p className="mt-2 text-slate-600">
              Pick up your matches, messages, and upcoming barter sessions.
            </p>
          </div>
        </div>
        {successMessage ? <p className="text-sm font-medium text-emerald-600">{successMessage}</p> : null}
        <form className="space-y-5" onSubmit={handleSubmit}>
          <Input
            label="Email"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="you@example.com"
            autoComplete="email"
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
            required
          />
          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 text-slate-600">
              <input type="checkbox" checked readOnly className="rounded border-slate-300" />
              Secure session enabled
            </label>
            <span className="font-medium text-slate-400">Password recovery coming soon</span>
          </div>
          {error ? <p className="text-sm font-medium text-rose-600">{error}</p> : null}
          <Button className="w-full py-4 text-base" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Logging in..." : "Log in to SkillBarter"}
          </Button>
        </form>
        <p className="text-sm text-slate-600">
          New here?{" "}
          <Link to="/register" className="font-semibold text-ink">
            Create an account
          </Link>
        </p>
      </Card>
    </div>
  );
}
