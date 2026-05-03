import { motion } from "framer-motion";
import {
  Check,
  CircleDot,
  MessageCircleHeart,
  MessageSquareText,
  SendHorizonal,
  Smile,
  UserPlus,
  Users,
  Wifi,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Badge, SectionHeading } from "../components/Layout";
import { Button, Card, EmptyState, Skeleton } from "../components/ui";
import { useRealtime } from "../context/RealtimeContext";
import { useToast } from "../context/ToastContext";
import {
  acceptMatchRequest,
  fetchMessages,
  fetchSocialOverview,
  rejectMatchRequest,
} from "../services/social";

const emojiOptions = ["👍", "🔥", "✨", "👏", "😊"];

function formatMessageTime(value) {
  return new Date(value).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

export default function ChatPage() {
  const { connected, markNotificationsRead, sendMessage, subscribe, unreadCount } = useRealtime();
  const { pushToast } = useToast();
  const [overview, setOverview] = useState({
    friends: [],
    incoming_requests: [],
    outgoing_requests: [],
  });
  const [activeFriendId, setActiveFriendId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeFriend, setActiveFriend] = useState(null);
  const [messageInput, setMessageInput] = useState("");
  const [error, setError] = useState("");
  const [isLoadingOverview, setIsLoadingOverview] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const bottomRef = useRef(null);

  const activeFriendName = activeFriend?.name || "Conversation";
  const isTyping = Boolean(messageInput.trim());

  const conversationPreview = useMemo(
    () =>
      overview.friends.map((friend) => ({
        ...friend,
        subtitle: friend.latest_message_preview || "No messages yet. Start the conversation.",
      })),
    [overview.friends],
  );

  useEffect(() => {
    markNotificationsRead();
  }, [markNotificationsRead]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    let isMounted = true;

    const loadOverview = async () => {
      try {
        const data = await fetchSocialOverview();
        if (!isMounted) {
          return;
        }
        setOverview(data);
        if (!activeFriendId && data.friends.length) {
          setActiveFriendId(data.friends[0].id);
        }
      } catch (requestError) {
        if (isMounted) {
          setError(requestError.message || "Unable to load your social graph.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingOverview(false);
        }
      }
    };

    loadOverview();

    return () => {
      isMounted = false;
    };
  }, [activeFriendId]);

  useEffect(() => {
    if (!activeFriendId) {
      setMessages([]);
      setActiveFriend(null);
      return;
    }

    let isMounted = true;
    setIsLoadingMessages(true);

    const loadMessages = async () => {
      try {
        const conversation = await fetchMessages(activeFriendId);
        if (isMounted) {
          setMessages(conversation.messages);
          setActiveFriend(conversation.conversation_with);
        }
      } catch (requestError) {
        if (isMounted) {
          setError(requestError.message || "Unable to load messages.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingMessages(false);
        }
      }
    };

    loadMessages();

    return () => {
      isMounted = false;
    };
  }, [activeFriendId]);

  useEffect(() => {
    const unsubscribe = subscribe((event) => {
      if (event.type === "message:new" && event.with_user?.id === activeFriendId) {
        setMessages((current) => [...current, event.message]);
      }

      if (event.type.startsWith("request:")) {
        fetchSocialOverview()
          .then((data) => {
            setOverview(data);
            if (!activeFriendId && data.friends.length) {
              setActiveFriendId(data.friends[0].id);
            }
          })
          .catch(() => {});
      }
    });

    return unsubscribe;
  }, [activeFriendId, subscribe]);

  const refreshOverview = async () => {
    const data = await fetchSocialOverview();
    setOverview(data);
    if (!activeFriendId && data.friends.length) {
      setActiveFriendId(data.friends[0].id);
    }
  };

  const handleAccept = async (requestId) => {
    try {
      await acceptMatchRequest(requestId);
      await refreshOverview();
      pushToast({
        title: "Request accepted",
        message: "Your new connection is ready to chat.",
        tone: "success",
      });
    } catch (requestError) {
      const nextMessage = requestError.message || "Unable to accept request.";
      setError(nextMessage);
      pushToast({
        title: "Accept failed",
        message: nextMessage,
        tone: "error",
      });
    }
  };

  const handleReject = async (requestId) => {
    try {
      await rejectMatchRequest(requestId);
      await refreshOverview();
      pushToast({
        title: "Request declined",
        message: "The request has been removed from your inbox.",
        tone: "info",
      });
    } catch (requestError) {
      const nextMessage = requestError.message || "Unable to reject request.";
      setError(nextMessage);
      pushToast({
        title: "Reject failed",
        message: nextMessage,
        tone: "error",
      });
    }
  };

  const handleSendMessage = (event) => {
    event.preventDefault();
    setError("");

    if (!activeFriendId || !messageInput.trim()) {
      return;
    }

    try {
      sendMessage({
        recipient_id: activeFriendId,
        content: messageInput.trim(),
      });
      setMessageInput("");
    } catch (requestError) {
      const nextMessage = requestError.message || "Unable to send message.";
      setError(nextMessage);
      pushToast({
        title: "Message failed",
        message: nextMessage,
        tone: "error",
      });
    }
  };

  const appendEmoji = (emoji) => {
    setMessageInput((current) => `${current}${emoji}`);
  };

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[0.38fr_0.62fr]">
        <Card className="space-y-6 overflow-hidden">
          <div className="flex items-start justify-between gap-4">
            <SectionHeading
              eyebrow="Social inbox"
              title="Conversations"
              body="Private chats, request approvals, and live conversation readiness."
            />
            <div className="space-y-2 text-right">
              <Badge tone={connected ? "mint" : "coral"}>{connected ? "Live" : "Reconnecting"}</Badge>
              {unreadCount ? <p className="text-xs text-slate-500 dark:text-slate-400">{unreadCount} unread</p> : null}
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
              <UserPlus className="h-4 w-4" />
              Pending requests
            </div>

            {overview.incoming_requests.length ? (
              overview.incoming_requests.map((request) => (
                <div
                  key={request.id}
                  className="rounded-[1.5rem] border border-slate-200/70 bg-slate-50/80 p-4 dark:border-slate-800/70 dark:bg-slate-900/70"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-semibold text-slate-950 dark:text-white">{request.sender.name}</p>
                      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{request.sender.email}</p>
                    </div>
                    <Badge tone="indigo">Request</Badge>
                  </div>
                  <div className="mt-4 flex gap-3">
                    <Button type="button" onClick={() => handleAccept(request.id)} icon={Check}>
                      Accept
                    </Button>
                    <Button type="button" variant="secondary" onClick={() => handleReject(request.id)}>
                      Reject
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-[1.5rem] border border-dashed border-slate-200/70 bg-slate-50/65 p-4 text-sm text-slate-500 dark:border-slate-800/70 dark:bg-slate-900/55 dark:text-slate-400">
                No pending requests right now.
              </div>
            )}
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
              <Users className="h-4 w-4" />
              Friends and connections
            </div>

            <div className="space-y-3">
              {isLoadingOverview ? (
                Array.from({ length: 4 }).map((_, index) => (
                  <div key={index} className="rounded-[1.5rem] border border-slate-200/70 p-4 dark:border-slate-800/70">
                    <Skeleton className="h-4 w-28" />
                    <Skeleton className="mt-3 h-4 w-full" />
                  </div>
                ))
              ) : conversationPreview.length ? (
                conversationPreview.map((friend) => (
                  <button
                    key={friend.id}
                    type="button"
                    onClick={() => setActiveFriendId(friend.id)}
                    className={`w-full rounded-[1.5rem] border p-4 text-left transition ${
                      activeFriendId === friend.id
                        ? "border-slate-950 bg-slate-950 text-white shadow-premium dark:border-white dark:bg-white dark:text-slate-950"
                        : "border-slate-200/70 bg-white/70 hover:border-slate-300 dark:border-slate-800/70 dark:bg-slate-950/65 dark:hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div
                          className={`flex h-10 w-10 items-center justify-center rounded-2xl ${
                            activeFriendId === friend.id
                              ? "bg-white/10 dark:bg-slate-900"
                              : "bg-slate-100 dark:bg-slate-900"
                          }`}
                        >
                          {friend.name
                            .split(" ")
                            .map((part) => part[0])
                            .join("")
                            .slice(0, 2)
                            .toUpperCase()}
                        </div>
                        <div>
                          <p className="font-semibold">{friend.name}</p>
                          <p className={`mt-1 text-sm ${activeFriendId === friend.id ? "text-white/70 dark:text-slate-500" : "text-slate-500 dark:text-slate-400"}`}>
                            {friend.subtitle}
                          </p>
                        </div>
                      </div>
                      <CircleDot className={`h-4 w-4 ${activeFriendId === friend.id ? "text-emerald-300" : "text-emerald-500"}`} />
                    </div>
                  </button>
                ))
              ) : (
                <div className="rounded-[1.5rem] border border-dashed border-slate-200/70 bg-slate-50/65 p-4 text-sm text-slate-500 dark:border-slate-800/70 dark:bg-slate-900/55 dark:text-slate-400">
                  Accept a request to unlock conversation.
                </div>
              )}
            </div>
          </div>
        </Card>

        <Card className="flex min-h-[720px] flex-col overflow-hidden bg-gradient-to-br from-white to-slate-50 dark:from-slate-950/90 dark:to-slate-900/90">
          <div className="flex flex-col gap-4 border-b border-slate-200/70 pb-5 dark:border-slate-800/70 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-slate-950 text-white dark:bg-white dark:text-slate-950">
                {activeFriendName
                  .split(" ")
                  .map((part) => part[0])
                  .join("")
                  .slice(0, 2)
                  .toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Realtime chat</p>
                <h2 className="mt-1 font-display text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">
                  {activeFriendName}
                </h2>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {activeFriend ? activeFriend.email : "Pick a friend from the left to start chatting."}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Badge tone={connected ? "mint" : "coral"}>{connected ? "Online" : "Offline"}</Badge>
              <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-600 dark:bg-slate-900 dark:text-slate-300">
                <Wifi className="h-3.5 w-3.5" />
                {connected ? "Socket connected" : "Reconnecting"}
              </div>
            </div>
          </div>

          <div className="mt-6 flex-1 space-y-4 overflow-y-auto pr-1">
            {isLoadingMessages ? (
              <div className="space-y-4">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div key={index} className={`flex ${index % 2 ? "justify-end" : "justify-start"}`}>
                    <Skeleton className={`h-16 rounded-[1.6rem] ${index % 2 ? "w-60" : "w-52"}`} />
                  </div>
                ))}
              </div>
            ) : messages.length ? (
              messages.map((message) => (
                <div key={message.id} className={`flex ${message.is_mine ? "justify-end" : "justify-start"}`}>
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`max-w-[82%] rounded-[1.6rem] px-4 py-3 text-sm leading-7 shadow-sm ${
                      message.is_mine
                        ? "bg-slate-950 text-white dark:bg-white dark:text-slate-950"
                        : "border border-slate-200/70 bg-white text-slate-700 dark:border-slate-800/70 dark:bg-slate-900 dark:text-slate-200"
                    }`}
                  >
                    <p>{message.content}</p>
                    <p className={`mt-2 text-xs ${message.is_mine ? "text-white/55 dark:text-slate-500" : "text-slate-400 dark:text-slate-500"}`}>
                      {formatMessageTime(message.created_at)}
                    </p>
                  </motion.div>
                </div>
              ))
            ) : (
              <div className="flex h-full items-center justify-center">
                <EmptyState
                  icon={MessageCircleHeart}
                  title="Start the conversation"
                  body="Use this chat like a premium intro room: align on goals, set expectations, and book your first exchange."
                />
              </div>
            )}

            {activeFriend && isTyping ? (
              <div className="flex justify-start">
                <div className="rounded-full bg-slate-100 px-4 py-2 text-xs font-medium text-slate-500 dark:bg-slate-900 dark:text-slate-400">
                  Drafting a thoughtful reply...
                </div>
              </div>
            ) : null}
            <div ref={bottomRef} />
          </div>

          <div className="mt-6 border-t border-slate-200/70 pt-5 dark:border-slate-800/70">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              {emojiOptions.map((emoji) => (
                <button
                  key={emoji}
                  type="button"
                  onClick={() => appendEmoji(emoji)}
                  className="rounded-full border border-slate-200/70 bg-white px-3 py-1.5 text-sm transition hover:border-slate-300 dark:border-slate-800/70 dark:bg-slate-950"
                >
                  {emoji}
                </button>
              ))}
              <div className="inline-flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
                <Smile className="h-4 w-4" />
                Quick reactions
              </div>
            </div>

            <form className="flex flex-col gap-3 sm:flex-row" onSubmit={handleSendMessage}>
              <input
                type="text"
                value={messageInput}
                onChange={(event) => setMessageInput(event.target.value)}
                placeholder={activeFriend ? `Message ${activeFriend.name}` : "Select a friend to start chatting"}
                disabled={!activeFriend}
                className="flex-1 rounded-[1.75rem] border border-slate-200/70 bg-white px-5 py-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-primary/40 focus:ring-4 focus:ring-primary/10 disabled:cursor-not-allowed disabled:bg-slate-100 dark:border-slate-800/70 dark:bg-slate-950 dark:text-white dark:disabled:bg-slate-900"
              />
              <Button type="submit" disabled={!activeFriend || !messageInput.trim()} icon={SendHorizonal}>
                Send
              </Button>
            </form>

            {error ? <p className="mt-4 text-sm font-medium text-rose-500">{error}</p> : null}
          </div>
        </Card>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {[
          {
            icon: MessageSquareText,
            title: "Private messaging",
            body: "Every accepted connection gets a dedicated realtime thread powered by your existing WebSocket backend.",
          },
          {
            icon: UserPlus,
            title: "Request flow",
            body: "Accept or reject match requests without leaving the inbox, keeping the social graph smooth and intentional.",
          },
          {
            icon: Wifi,
            title: "Live state",
            body: "Unread notifications, connection status, and recent activity stay visible so chat feels instant and trustworthy.",
          },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.title}>
              <div className="mb-4 inline-flex rounded-2xl bg-indigo-50 p-3 text-primary dark:bg-indigo-950/60 dark:text-indigo-200">
                <Icon className="h-5 w-5" />
              </div>
              <p className="font-display text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">
                {item.title}
              </p>
              <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-400">{item.body}</p>
            </Card>
          );
        })}
      </section>
    </div>
  );
}
