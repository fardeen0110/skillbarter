import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute() {
  const location = useLocation();
  const { hasToken, isInitializing, user } = useAuth();

  if (isInitializing && hasToken) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-600 shadow-sm">
          Restoring your session...
        </div>
      </div>
    );
  }

  if (!hasToken || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
