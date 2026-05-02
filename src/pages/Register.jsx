import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Badge } from "../components/Layout";
import { Button, Card, Input } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { registerUser } from "../services/auth";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
  });
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
      await registerUser({
        name: `${formData.firstName} ${formData.lastName}`.trim(),
        email: formData.email.trim(),
        password: formData.password,
      });
      navigate("/login", {
        replace: true,
        state: { message: "Account created successfully. Please log in." },
      });
    } catch (requestError) {
      setError(requestError.message || "Unable to create your account. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-lg">
      <Card className="space-y-8 bg-white/90">
        <div className="space-y-4">
          <Badge tone="coral">Start for free</Badge>
          <div>
            <h1 className="font-display text-4xl font-semibold tracking-tight text-ink">Create account</h1>
            <p className="mt-2 text-slate-600">
              Join the network and begin trading real skills with ambitious peers.
            </p>
          </div>
        </div>
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="grid gap-5 sm:grid-cols-2">
            <Input
              label="First name"
              type="text"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              placeholder="Alex"
              autoComplete="given-name"
              required
            />
            <Input
              label="Last name"
              type="text"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              placeholder="Jordan"
              autoComplete="family-name"
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
            required
          />
          <Input
            label="Password"
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Choose a password"
            helper="Use at least 8 characters to protect your account."
            autoComplete="new-password"
            required
          />
          {error ? <p className="text-sm font-medium text-rose-600">{error}</p> : null}
          <Button className="w-full py-4 text-base" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating account..." : "Create my account"}
          </Button>
        </form>
        <p className="text-sm text-slate-600">
          Already a member?{" "}
          <Link to="/login" className="font-semibold text-ink">
            Log in
          </Link>
        </p>
      </Card>
    </div>
  );
}
