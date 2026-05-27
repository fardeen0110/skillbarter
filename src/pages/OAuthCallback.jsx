import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Card, Spinner } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { clearSession, fetchCurrentUser, saveAccessToken } from "../services/auth";

export default function OAuthCallbackPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const { pushToast } = useToast();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get("token");
    const nextPath = params.get("next") || "/dashboard";
    const oauthError = params.get("error");

    if (oauthError) {
      clearSession();
      pushToast({
        title: "Google sign-in failed",
        message: oauthError,
        tone: "error",
      });
      navigate("/login", { replace: true });
      return;
    }

    if (!token) {
      clearSession();
      pushToast({
        title: "OAuth failed",
        message: "Missing login token from provider callback.",
        tone: "error",
      });
      navigate("/login", { replace: true });
      return;
    }

    const finalize = async () => {
      try {
        saveAccessToken(token);
        const user = await fetchCurrentUser();
        setUser(user);
        pushToast({
          title: "Signed in",
          message: "Your OAuth login completed successfully.",
          tone: "success",
        });
        navigate(nextPath, { replace: true });
      } catch (error) {
        clearSession();
        pushToast({
          title: "OAuth failed",
          message: error.message || "Unable to complete OAuth login.",
          tone: "error",
        });
        navigate("/login", { replace: true });
      }
    };

    finalize();
  }, [location.search, navigate, pushToast, setUser]);

  return (
    <div className="bg-app flex min-h-screen items-center justify-center px-4">
      <Card className="flex items-center gap-4">
        <Spinner />
        <div>
          <p className="font-semibold text-slate-950 dark:text-white">Completing sign-in</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">Please wait while we finalize your account.</p>
        </div>
      </Card>
    </div>
  );
}
