import { useEffect, useMemo, useRef, useState } from "react";
import { Badge, SectionHeading } from "../components/Layout";
import { Button, Card } from "../components/ui";
import { useRealtime } from "../context/RealtimeContext";
import {
  acceptMatchRequest,
  fetchMessages,
  fetchSocialOverview,
  rejectMatchRequest,
} from "../services/social";

export default function ChatPage() {
  const { connected, markNotificationsRead, sendMessage, subscribe, unreadCount } = useRealtime();
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

  const handleAccept = async (requestId) => {
    try {
      await acceptMatchRequest(requestId);
      const data = await fetchSocialOverview();
      setOverview(data);
      if (!activeFriendId && data.friends.length) {
        setActiveFriendId(data.friends[0].id);
      }
    } catch (requestError) {
      setError(requestError.message || "Unable to accept request.");
    }
  };

  const handleReject = async (requestId) => {
    try {
      await rejectMatchRequest(requestId);
      const data = await fetchSocialOverview();
      setOverview(data);
    } catch (requestError) {
      setError(requestError.message || "Unable to reject request.");
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
      setError(requestError.message || "Unable to send message.");
    }
  };

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[0.36fr_0.64fr]">
        <Card className="space-y-6 bg-white/90">
          <div className="flex items-start justify-between gap-4">
            <SectionHeading
              eyebrow="Social Inbox"
              title="Conversations"
              body="Accepted barter partners, pending requests, and live alerts in one place."
            />
            <div className="space-y-2 text-right">
              <Badge tone={connected ? "mint" : "coral"}>{connected ? "Live" : "Reconnecting"}</Badge>
              {unreadCount ? <p className="text-xs text-slate-500">{unreadCount} unread alerts</p> : null}
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
              Pending Requests
            </p>
            {overview.incoming_requests.length ? (
              overview.incoming_requests.map((request) => (
                <div key={request.id} className="rounded-[1.5rem] border border-slate-100 bg-slate-50 p-4">
                  <p className="font-semibold text-ink">{request.sender.name}</p>
                  <p className="mt-1 text-sm text-slate-500">{request.sender.email}</p>
                  <div className="mt-4 flex gap-3">
                    <Button type="button" onClick={() => handleAccept(request.id)}>
                      Accept
                    </Button>
                    <Button type="button" variant="secondary" onClick={() => handleReject(request.id)}>
                      Reject
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <p className="rounded-[1.5rem] bg-slate-50 p-4 text-sm text-slate-500">
                No pending requests right now.
              </p>
            )}
          </div>

          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">Friends</p>
            <div className="space-y-3">
              {isLoadingOverview ? (
                <p className="rounded-[1.5rem] bg-slate-50 p-4 text-sm text-slate-500">
                  Loading your conversations...
                </p>
              ) : conversationPreview.length ? (
                conversationPreview.map((friend) => (
                  <button
                    key={friend.id}
                    type="button"
                    onClick={() => setActiveFriendId(friend.id)}
                    className={`w-full rounded-[1.5rem] border p-4 text-left transition ${
                      activeFriendId === friend.id
                        ? "border-ink bg-ink text-white"
                        : "border-slate-100 bg-white hover:border-slate-200"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-semibold">{friend.name}</p>
                      <Badge tone={activeFriendId === friend.id ? "gold" : "sky"}>
                        {friend.last_message_at ? "Active" : "New"}
                      </Badge>
                    </div>
                    <p className={`mt-2 text-sm ${activeFriendId === friend.id ? "text-white/70" : "text-slate-500"}`}>
                      {friend.subtitle}
                    </p>
                  </button>
                ))
              ) : (
                <p className="rounded-[1.5rem] bg-slate-50 p-4 text-sm text-slate-500">
                  Accept a match request to unlock chat.
                </p>
              )}
            </div>
          </div>
        </Card>

        <Card className="flex min-h-[680px] flex-col overflow-hidden bg-gradient-to-br from-white to-slate-50">
          <div className="flex items-center justify-between border-b border-slate-100 pb-5">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Realtime Chat</p>
              <h2 className="mt-2 font-display text-3xl font-semibold tracking-tight text-ink">
                {activeFriendName}
              </h2>
              <p className="mt-2 text-sm text-slate-500">
                {activeFriend ? activeFriend.email : "Pick a friend from the left to start chatting."}
              </p>
            </div>
            <Badge tone={connected ? "mint" : "coral"}>
              {connected ? "Messages live" : "Waiting for socket"}
            </Badge>
          </div>

          <div className="mt-6 flex-1 space-y-4 overflow-y-auto pr-1">
            {isLoadingMessages ? (
              <p className="text-sm text-slate-500">Loading conversation...</p>
            ) : messages.length ? (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.is_mine ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-[1.5rem] px-4 py-3 text-sm leading-6 shadow-sm ${
                      message.is_mine
                        ? "bg-ink text-white"
                        : "border border-slate-100 bg-white text-slate-700"
                    }`}
                  >
                    <p>{message.content}</p>
                    <p className={`mt-2 text-xs ${message.is_mine ? "text-white/60" : "text-slate-400"}`}>
                      {new Date(message.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex h-full items-center justify-center">
                <div className="max-w-md rounded-[2rem] border border-dashed border-slate-200 bg-white/80 p-8 text-center">
                  <p className="font-display text-2xl font-semibold text-ink">Start the conversation</p>
                  <p className="mt-3 text-sm leading-7 text-slate-500">
                    Send a thoughtful opener, set expectations, and schedule your first skill swap.
                  </p>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <form className="mt-6 flex flex-col gap-3 border-t border-slate-100 pt-5 sm:flex-row" onSubmit={handleSendMessage}>
            <input
              type="text"
              value={messageInput}
              onChange={(event) => setMessageInput(event.target.value)}
              placeholder={activeFriend ? `Message ${activeFriend.name}` : "Select a friend to start chatting"}
              disabled={!activeFriend}
              className="flex-1 rounded-full border border-slate-200 bg-white px-5 py-3 text-sm text-slate-900 outline-none focus:border-slate-400 focus:ring-4 focus:ring-slate-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            />
            <Button type="submit" disabled={!activeFriend || !messageInput.trim()}>
              Send message
            </Button>
          </form>

          {error ? <p className="mt-4 text-sm font-medium text-rose-600">{error}</p> : null}
        </Card>
      </section>
    </div>
  );
}
