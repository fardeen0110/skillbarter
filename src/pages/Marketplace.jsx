import { BriefcaseBusiness, Plus, Search, SendHorizonal } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Badge, SectionHeading } from "../components/Layout";
import { Button, Card, EmptyState, Input, Select, Skeleton, Textarea } from "../components/ui";
import { useToast } from "../context/ToastContext";
import { fetchMatchmakingSkills } from "../services/auth";
import {
  applyToMarketplaceRequest,
  createMarketplaceRequest,
  fetchMarketplaceRequests,
} from "../services/platform";

export default function MarketplacePage() {
  const { pushToast } = useToast();
  const loadMoreRef = useRef(null);
  const [skills, setSkills] = useState([]);
  const [items, setItems] = useState([]);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [skill, setSkill] = useState("");
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [applicationMessage, setApplicationMessage] = useState({});
  const [createForm, setCreateForm] = useState({
    skill: "",
    title: "",
    description: "",
    city: "",
    availability: "",
  });

  useEffect(() => {
    fetchMatchmakingSkills()
      .then((nextSkills) => {
        setSkills(nextSkills);
        setCreateForm((current) => ({ ...current, skill: current.skill || nextSkills[0] || "" }));
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    fetchMarketplaceRequests({ query, status, skill, page: 1 })
      .then((data) => {
        if (!isMounted) {
          return;
        }
        setItems(data.items);
        setHasMore(data.items.length < data.total);
        setPage(1);
      })
      .catch((error) => {
        pushToast({
          title: "Unable to load marketplace",
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
  }, [pushToast, query, skill, status]);

  useEffect(() => {
    if (!hasMore || isLoading) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries[0]?.isIntersecting) {
          return;
        }
        fetchMarketplaceRequests({ query, status, skill, page: page + 1 })
          .then((data) => {
            setItems((current) => [...current, ...data.items]);
            setPage((current) => current + 1);
            setHasMore(items.length + data.items.length < data.total);
          })
          .catch(() => {});
      },
      { rootMargin: "200px" },
    );

    const node = loadMoreRef.current;
    if (node) {
      observer.observe(node);
    }

    return () => observer.disconnect();
  }, [hasMore, isLoading, items.length, page, query, skill, status]);

  const handleCreate = async (event) => {
    event.preventDefault();
    setIsCreating(true);
    try {
      const created = await createMarketplaceRequest(createForm);
      setItems((current) => [created, ...current]);
      setCreateForm((current) => ({ ...current, title: "", description: "", city: "", availability: "" }));
      pushToast({
        title: "Request posted",
        message: "Your marketplace request is live.",
        tone: "success",
      });
    } catch (error) {
      pushToast({
        title: "Unable to create request",
        message: error.message,
        tone: "error",
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleApply = async (requestId) => {
    try {
      await applyToMarketplaceRequest(requestId, {
        message: applicationMessage[requestId] || "",
      });
      pushToast({
        title: "Application sent",
        message: "The request owner has been notified.",
        tone: "success",
      });
    } catch (error) {
      pushToast({
        title: "Unable to apply",
        message: error.message,
        tone: "error",
      });
    }
  };

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <Card className="space-y-6">
          <SectionHeading
            eyebrow="Marketplace"
            title="Post real learning requests and attract the right collaborators"
            body="This is now a true marketplace surface backed by PostgreSQL instead of placeholder cards."
          />
          <form className="space-y-4" onSubmit={handleCreate}>
            <Select label="Skill" value={createForm.skill} onChange={(event) => setCreateForm((current) => ({ ...current, skill: event.target.value }))}>
              {skills.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </Select>
            <Input label="Title" value={createForm.title} onChange={(event) => setCreateForm((current) => ({ ...current, title: event.target.value }))} placeholder="Need help improving onboarding copy" />
            <Textarea label="Description" value={createForm.description} onChange={(event) => setCreateForm((current) => ({ ...current, description: event.target.value }))} placeholder="Describe the exact outcome you want and how an exchange could work." />
            <div className="grid gap-4 md:grid-cols-2">
              <Input label="City" value={createForm.city} onChange={(event) => setCreateForm((current) => ({ ...current, city: event.target.value }))} placeholder="Bengaluru" />
              <Input label="Availability" value={createForm.availability} onChange={(event) => setCreateForm((current) => ({ ...current, availability: event.target.value }))} placeholder="Weeknights, Sunday mornings" />
            </div>
            <Button type="submit" icon={Plus} isLoading={isCreating}>
              {isCreating ? "Publishing request" : "Post learning request"}
            </Button>
          </form>
        </Card>

        <Card className="space-y-5">
          <SectionHeading
            eyebrow="Discover"
            title="Search and filter live requests"
            body="Filter by skill, status, and keywords. Results page in incrementally as you scroll."
          />
          <div className="grid gap-4 md:grid-cols-[1fr_0.24fr_0.24fr]">
            <Input label="Search" value={query} onChange={(event) => setQuery(event.target.value)} icon={Search} placeholder="Search titles, cities, or goals" />
            <Select label="Status" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All</option>
              <option value="open">Open</option>
              <option value="closed">Closed</option>
            </Select>
            <Select label="Skill" value={skill} onChange={(event) => setSkill(event.target.value)}>
              <option value="">All</option>
              {skills.map((item) => (
                <option key={item} value={item.toLowerCase().replaceAll(" ", "-")}>
                  {item}
                </option>
              ))}
            </Select>
          </div>
        </Card>
      </section>

      <section className="grid gap-6">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, index) => (
            <Card key={index} className="space-y-4">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-24 w-full" />
            </Card>
          ))
        ) : items.length ? (
          items.map((item) => (
            <Card key={item.id} className="space-y-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="font-display text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">{item.title}</p>
                  <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    {item.creator.name} • {item.skill.name} • {item.city || "Remote"}
                  </p>
                </div>
                <Badge tone={item.status === "open" ? "mint" : "coral"}>{item.status}</Badge>
              </div>
              <p className="text-sm leading-7 text-slate-600 dark:text-slate-400">{item.description}</p>
              <div className="grid gap-4 md:grid-cols-[1fr_auto]">
                <Textarea
                  label="Application message"
                  value={applicationMessage[item.id] || ""}
                  onChange={(event) =>
                    setApplicationMessage((current) => ({ ...current, [item.id]: event.target.value }))
                  }
                  placeholder="Explain why you're a strong fit for this request."
                />
                <div className="flex items-end">
                  <Button type="button" icon={SendHorizonal} onClick={() => handleApply(item.id)}>
                    Apply
                  </Button>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <EmptyState
            icon={BriefcaseBusiness}
            title="No requests found"
            body="Try a broader search or post the first request in this category."
          />
        )}
        <div ref={loadMoreRef} className="h-10" />
      </section>
    </div>
  );
}
