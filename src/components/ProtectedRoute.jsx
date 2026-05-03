import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Spinner } from "./ui";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute() {
  const location = useLocation();
  const { hasToken, isInitializing, user } = useAuth();

  if (isInitializing && hasToken) {
    return (
      <div className="bg-app flex min-h-screen items-center justify-center px-4">
        <div className="glass-panel flex items-center gap-3 rounded-full border border-slate-200/70 px-5 py-3 text-sm font-semibold text-slate-600 shadow-premium dark:border-slate-800/80 dark:text-slate-300">
          <Spinner className="h-4 w-4" />
          Restoring your workspace...
        </div>
      </div>
    );
  }

  if (!hasToken || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
