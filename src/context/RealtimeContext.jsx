import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "./AuthContext";
import { getChatWebSocketUrl } from "../services/social";

const RealtimeContext = createContext(null);

export function RealtimeProvider({ children }) {
  const { isAuthenticated, user } = useAuth();
  const socketRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const listenersRef = useRef(new Set());
  const [connected, setConnected] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!isAuthenticated || !user) {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
      setConnected(false);
      return undefined;
    }

    let isMounted = true;

    const connect = () => {
      const socket = new WebSocket(getChatWebSocketUrl());
      socketRef.current = socket;

      socket.onopen = () => {
        if (isMounted) {
          setConnected(true);
        }
      };

      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data);

        listenersRef.current.forEach((listener) => listener(payload));

        if (payload.alert || payload.message) {
          setNotifications((current) => [
            {
              id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
              type: payload.type,
              text: payload.alert || payload.message,
            },
            ...current,
          ].slice(0, 20));
          setUnreadCount((count) => count + 1);
        }
      };

      socket.onclose = () => {
        if (!isMounted) {
          return;
        }
        setConnected(false);
        reconnectTimerRef.current = window.setTimeout(connect, 2000);
      };
    };

    connect();

    return () => {
      isMounted = false;
      setConnected(false);
      if (reconnectTimerRef.current) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [isAuthenticated, user]);

  const value = useMemo(
    () => ({
      connected,
      notifications,
      unreadCount,
      sendMessage(payload) {
        if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
          throw new Error("Realtime connection is not ready.");
        }
        socketRef.current.send(JSON.stringify(payload));
      },
      subscribe(listener) {
        listenersRef.current.add(listener);
        return () => listenersRef.current.delete(listener);
      },
      markNotificationsRead() {
        setUnreadCount(0);
      },
      clearNotifications() {
        setNotifications([]);
        setUnreadCount(0);
      },
    }),
    [connected, notifications, unreadCount],
  );

  return <RealtimeContext.Provider value={value}>{children}</RealtimeContext.Provider>;
}

export function useRealtime() {
  const context = useContext(RealtimeContext);

  if (!context) {
    throw new Error("useRealtime must be used within a RealtimeProvider");
  }

  return context;
}
