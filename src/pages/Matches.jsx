import { motion } from "framer-motion";
import {
  ArrowRight,
  Filter,
  Gauge,
  LoaderCircle,
  MessageCircle,
  SearchCheck,
  Send,
  Sparkles,
  Stars,
  Users2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Badge, SectionHeading } from "../components/Layout";
import { Button, Card, EmptyState, Select, Skeleton } from "../components/ui";
import { useToast } from "../context/ToastContext";
import { fetchMatchmakingSkills, requestMatches } from "../services/auth";
import { fetchSocialOverview, sendMatchRequest } from "../services/social";

function MatchCardSkeleton() {
  return (
    <Card className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-3">
          <Skeleton className="h-5 w-36" />
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-4 w-24" />
        </div>
        <Skeleton className="h-10 w-20 rounded-full" />
      </div>
      <Skeleton className="h-4 w-full" />
      <div className="flex justify-between gap-3">
        <Skeleton className="h-10 w-32 rounded-2xl" />
        <Skeleton className="h-10 w-28 rounded-2xl" />
      </div>
    </Card>
  );
}

export default function MatchesPage() {
  const { pushToast } = useToast();
  const [skills, setSkills] = useState([]);
  const [formData, setFormData] = useState({
    skill_offer: "React",
    skill_want: "Product Strategy",
  });
  const [matches, setMatches] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [isLoadingSkills, setIsLoadingSkills] = useState(true);
  const [relationshipState, setRelationshipState] = useState({});

  useEffect(() => {
    let isMounted = true;

    const loadSkills = async () => {
      try {
        const nextSkills = await fetchMatchmakingSkills();
        if (isMounted) {
          setSkills(nextSkills);
          setFormData((current) => ({
            skill_offer: nextSkills.includes(current.skill_offer) ? current.skill_offer : nextSkills[0],
            skill_want:
              nextSkills.includes(current.skill_want) && current.skill_want !== current.skill_offer
                ? current.skill_want
                : nextSkills[1] || nextSkills[0],
          }));
        }
      } catch (requestError) {
        if (isMounted) {
          setError(requestError.message || "Unable to load skills.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingSkills(false);
        }
      }
    };

    loadSkills();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    const loadSocialState = async () => {
      try {
        const overview = await fetchSocialOverview();
        if (!isMounted) {
          return;
        }

        const nextState = {};
        overview.friends.forEach((friend) => {
          nextState[friend.id] = "friend";
        });
        overview.outgoing_requests.forEach((request) => {
          nextState[request.receiver.id] = "pending";
        });
        overview.incoming_requests.forEach((request) => {
          nextState[request.sender.id] = "incoming";
        });
        setRelationshipState(nextState);
      } catch {
        // Non-blocking for the matchmaking surface.
      }
    };

    loadSocialState();

    return () => {
      isMounted = false;
    };
  }, []);

  const scoreSummary = useMemo(() => {
    if (!matches.length) {
      return null;
    }

    const averageScore = Math.round(matches.reduce((total, match) => total + match.score, 0) / matches.length);

    return { averageScore, strongestMatch: matches[0] };
  }, [matches]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => {
      const nextState = { ...current, [name]: value };

      if (nextState.skill_offer === nextState.skill_want) {
        nextState[name === "skill_offer" ? "skill_want" : "skill_offer"] =
          skills.find((skill) => skill !== value) || value;
      }

      return nextState;
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");

    try {
      const nextMatches = await requestMatches(formData);
      setMatches(nextMatches);
      pushToast({
        title: "Matches generated",
        message: "Your top five recommendations are ready.",
        tone: "success",
      });
    } catch (requestError) {
      const nextMessage = requestError.message || "Unable to generate matches.";
      setError(nextMessage);
      setMatches([]);
      pushToast({
        title: "Matchmaking failed",
        message: nextMessage,
        tone: "error",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSendRequest = async (match) => {
    try {
      await sendMatchRequest(match.user_id);
      setRelationshipState((current) => ({ ...current, [match.user_id]: "pending" }));
      pushToast({
        title: "Request sent",
        message: `Your request to ${match.name} is on the way.`,
        tone: "success",
      });
    } catch (requestError) {
      const nextMessage = requestError.message || "Unable to send match request.";
      setError(nextMessage);
      pushToast({
        title: "Request failed",
        message: nextMessage,
        tone: "error",
      });
    }
  };

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="overflow-hidden bg-slate-950 text-white shadow-float dark:bg-slate-900">
          <div className="absolute inset-0 bg-spotlight opacity-70" />
          <div className="relative space-y-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div className="space-y-4">
                <Badge tone="mint">AI Matchmaking</Badge>
                <div>
                  <h1 className="max-w-3xl font-display text-4xl font-semibold tracking-tight sm:text-5xl">
                    Generate stunningly relevant barter partners in one move.
                  </h1>
                  <p className="mt-4 max-w-2xl text-base leading-7 text-white/70">
                    Your backend model still drives the logic. This UI simply turns that prediction engine into a premium discovery flow.
                  </p>
                </div>
              </div>
              <div className="rounded-[1.5rem] border border-white/10 bg-white/8 px-4 py-4 backdrop-blur-sm">
                <p className="text-xs uppercase tracking-[0.24em] text-white/45">Signals used</p>
                <p className="mt-2 text-sm text-white/72">Similarity, availability, ratings, interaction preference, and prior exchange history.</p>
              </div>
            </div>

            <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
              <Select
                label="Skill you offer"
                name="skill_offer"
                value={formData.skill_offer}
                onChange={handleChange}
                disabled={isLoadingSkills}
              >
                {skills.map((skill) => (
                  <option key={skill} value={skill}>
                    {skill}
                  </option>
                ))}
              </Select>
              <Select
                label="Skill you want"
                name="skill_want"
                value={formData.skill_want}
                onChange={handleChange}
                disabled={isLoadingSkills}
              >
                {skills.map((skill) => (
                  <option key={skill} value={skill}>
                    {skill}
                  </option>
                ))}
              </Select>

              <div className="md:col-span-2 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="inline-flex items-center gap-2 text-sm text-white/70">
                  <Filter className="h-4 w-4" />
                  Premium discovery tuned to your exact pairing.
                </div>
                <Button
                  type="submit"
                  variant="accent"
                  className="px-6"
                  icon={SearchCheck}
                  isLoading={isSubmitting}
                  disabled={isSubmitting || isLoadingSkills || skills.length < 2}
                >
                  {isLoadingSkills ? "Loading skills" : isSubmitting ? "Finding matches" : "Generate top matches"}
                </Button>
              </div>
              {error ? <p className="md:col-span-2 text-sm font-medium text-rose-300">{error}</p> : null}
            </form>
          </div>
        </Card>

        <Card className="space-y-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
                Compatibility snapshot
              </p>
              <p className="mt-3 font-display text-5xl font-semibold tracking-tight text-slate-950 dark:text-white">
                {scoreSummary ? `${scoreSummary.averageScore}%` : "--"}
              </p>
            </div>
            <div className="rounded-3xl bg-indigo-50 p-3 text-primary dark:bg-indigo-950/60 dark:text-indigo-200">
              <Gauge className="h-6 w-6" />
            </div>
          </div>

          {scoreSummary ? (
            <div className="space-y-4">
              <div className="rounded-[1.75rem] border border-slate-200/70 bg-slate-50/80 px-5 py-5 dark:border-slate-800/70 dark:bg-slate-900/70">
                <p className="text-sm text-slate-500 dark:text-slate-400">Best introduction right now</p>
                <p className="mt-2 font-display text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">
                  {scoreSummary.strongestMatch.name}
                </p>
                <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-400">
                  Offers {scoreSummary.strongestMatch.skill} at {scoreSummary.strongestMatch.score}% predicted success.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                {[
                  { icon: Stars, label: "Model tuned", value: "Random Forest" },
                  { icon: Users2, label: "Returned", value: "Top 5" },
                  { icon: Sparkles, label: "Experience", value: "Polished UI" },
                ].map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.label} className="rounded-2xl border border-slate-200/70 px-4 py-4 dark:border-slate-800/70">
                      <Icon className="h-4 w-4 text-primary" />
                      <p className="mt-3 text-xs uppercase tracking-[0.22em] text-slate-400">{item.label}</p>
                      <p className="mt-1 text-sm font-semibold text-slate-950 dark:text-white">{item.value}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <SectionHeading
              eyebrow="Ready to search"
              title="Tell us what you can teach and what you want to learn."
              body="We will generate ranked introductions, complete with compatibility scores and social actions."
            />
          )}
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.34fr]">
        <div className="grid gap-6 md:grid-cols-2">
          {isSubmitting ? (
            Array.from({ length: 4 }).map((_, index) => <MatchCardSkeleton key={index} />)
          ) : matches.length ? (
            matches.map((match, index) => {
              const relationship = relationshipState[match.user_id];
              return (
                <motion.div
                  key={`${match.user_id}-${match.name}`}
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.06 }}
                >
                  <Card className={index === 0 ? "bg-slate-950 text-white shadow-float dark:bg-slate-900" : ""}>
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-display text-2xl font-semibold tracking-tight">{match.name}</p>
                        <p className={`mt-2 text-sm ${index === 0 ? "text-white/65" : "text-slate-500 dark:text-slate-400"}`}>
                          Offers {match.skill}
                        </p>
                        <p className={`text-sm ${index === 0 ? "text-white/65" : "text-slate-500 dark:text-slate-400"}`}>
                          Great fit for learning {formData.skill_want}
                        </p>
                      </div>
                      <Badge tone={index === 0 ? "gold" : "mint"}>{match.score}% match</Badge>
                    </div>

                    <div className="mt-6 flex flex-wrap gap-2">
                      {[match.skill, formData.skill_offer, formData.skill_want].map((tag) => (
                        <span
                          key={`${match.name}-${tag}`}
                          className={index === 0
                            ? "rounded-full border border-white/12 bg-white/8 px-3 py-1 text-xs text-white/72"
                            : "rounded-full border border-slate-200/70 bg-slate-50 px-3 py-1 text-xs text-slate-600 dark:border-slate-800/70 dark:bg-slate-900 dark:text-slate-300"}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>

                    <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <p className={`text-sm ${index === 0 ? "text-white/65" : "text-slate-500 dark:text-slate-400"}`}>
                        Exchange your {formData.skill_offer} expertise for {formData.skill_want}.
                      </p>
                      {relationship === "friend" ? (
                        <Button
                          as="link"
                          to="/chat"
                          variant={index === 0 ? "secondary" : "primary"}
                          className={index === 0 ? "border-white/15 bg-white text-slate-950 hover:bg-slate-100" : ""}
                          icon={MessageCircle}
                        >
                          Open chat
                        </Button>
                      ) : (
                        <Button
                          type="button"
                          onClick={() => handleSendRequest(match)}
                          disabled={relationship === "pending"}
                          variant={index === 0 ? "secondary" : "primary"}
                          className={index === 0 ? "border-white/15 bg-white text-slate-950 hover:bg-slate-100" : ""}
                          icon={relationship === "pending" ? LoaderCircle : Send}
                        >
                          {relationship === "incoming"
                            ? "Request waiting"
                            : relationship === "pending"
                              ? "Request sent"
                              : "Send request"}
                        </Button>
                      )}
                    </div>
                  </Card>
                </motion.div>
              );
            })
          ) : (
            <div className="md:col-span-2">
              <EmptyState
                icon={SearchCheck}
                title="No matches yet"
                body="Choose your offered skill and learning goal above, then generate your first premium set of recommendations."
                action={<Button type="button" variant="secondary">Start with the filters above</Button>}
              />
            </div>
          )}
        </div>

        <Card className="space-y-5">
          <SectionHeading
            eyebrow="What improves a match"
            title="The ranking engine is looking for confidence, overlap, and momentum."
            body="These factors make introductions more likely to turn into successful exchanges."
          />
          <div className="space-y-3">
            {[
              "Mutual skill complementarity has the strongest effect on ranking.",
              "Availability overlap improves follow-through and conversation speed.",
              "Higher user rating averages and prior exchange history boost trust.",
              "Once connected, accepted requests open into realtime chat instantly.",
            ].map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-slate-200/70 bg-slate-50/80 px-4 py-4 text-sm leading-7 text-slate-600 dark:border-slate-800/70 dark:bg-slate-900/70 dark:text-slate-300"
              >
                {item}
              </div>
            ))}
          </div>
          <Link to="/chat" className="inline-flex items-center gap-2 text-sm font-semibold text-primary">
            Move to conversations <ArrowRight className="h-4 w-4" />
          </Link>
        </Card>
      </section>
    </div>
  );
}
