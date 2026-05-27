import { BellRing, CheckCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { SectionHeading } from "../components/Layout";
import { Button, Card, EmptyState, Skeleton } from "../components/ui";
import { useToast } from "../context/ToastContext";
import { fetchNotifications } from "../services/auth";
import { markNotificationAsRead } from "../services/platform";

export default function NotificationsPage() {
  const { pushToast } = useToast();
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    fetchNotifications()
      .then((data) => {
        if (isMounted) {
          setItems(data);
        }
      })
      .catch((error) => {
        pushToast({
          title: "Unable to load notifications",
          message: error.message,
          tone: "error",
        });
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [pushToast]);

  const handleMarkRead = async (notificationId) => {
    try {
      await markNotificationAsRead(notificationId);
      setItems((current) =>
        current.map((item) => (item.id === notificationId ? { ...item, is_read: true } : item)),
      );
    } catch (error) {
      pushToast({
        title: "Unable to update notification",
        message: error.message,
        tone: "error",
      });
    }
  };

  return (
    <div className="space-y-6">
      <SectionHeading
        eyebrow="Notification center"
        title="Everything that needs your attention"
        body="Realtime alerts and persisted product notifications now live in one feed."
      />

      <div className="grid gap-4">
        {isLoading ? (
          Array.from({ length: 5 }).map((_, index) => (
            <Card key={index} className="space-y-3">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-48" />
            </Card>
          ))
        ) : items.length ? (
          items.map((item) => (
            <Card key={item.id} className={item.is_read ? "opacity-75" : ""}>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="space-y-2">
                  <p className="font-semibold text-slate-950 dark:text-white">{item.title}</p>
                  <p className="text-sm leading-7 text-slate-600 dark:text-slate-400">{item.body}</p>
                  <p className="text-xs uppercase tracking-[0.22em] text-slate-400">{item.type}</p>
                </div>
                {!item.is_read ? (
                  <Button type="button" variant="secondary" icon={CheckCheck} onClick={() => handleMarkRead(item.id)}>
                    Mark read
                  </Button>
                ) : null}
              </div>
            </Card>
          ))
        ) : (
          <EmptyState
            icon={BellRing}
            title="No notifications yet"
            body="Once people message you, review you, or respond to requests, updates will appear here."
          />
        )}
      </div>
    </div>
  );
}
