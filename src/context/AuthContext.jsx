import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import {
  clearSession,
  fetchCurrentUser,
  getStoredUser,
  hasStoredToken,
  loginUser,
} from "../services/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser());
  const [isInitializing, setIsInitializing] = useState(true);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  const refreshCurrentUser = useCallback(async () => {
    const currentUser = await fetchCurrentUser();
    setUser(currentUser);
    return currentUser;
  }, []);

  const login = useCallback(async (credentials) => {
    const response = await loginUser(credentials);
    setUser(response.user);
    return response;
  }, []);

  useEffect(() => {
    let isMounted = true;

    const bootstrap = async () => {
      if (!hasStoredToken()) {
        if (isMounted) {
          setIsInitializing(false);
        }
        return;
      }

      try {
        await refreshCurrentUser();
      } catch {
        logout();
        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setIsInitializing(false);
        }
      }
    };

    bootstrap();

    return () => {
      isMounted = false;
    };
  }, [logout, refreshCurrentUser]);

  const value = useMemo(
    () => ({
      user,
      isInitializing,
      hasToken: hasStoredToken(),
      isAuthenticated: Boolean(user && hasStoredToken()),
      login,
      logout,
      refreshCurrentUser,
      setUser,
    }),
    [isInitializing, login, logout, refreshCurrentUser, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
