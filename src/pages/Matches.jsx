import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Badge } from "../components/Layout";
import { Button, Card } from "../components/ui";
import { fetchMatchmakingSkills, requestMatches } from "../services/auth";
import { fetchSocialOverview, sendMatchRequest } from "../services/social";

export default function MatchesPage() {
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

    const averageScore = Math.round(
      matches.reduce((total, match) => total + match.score, 0) / matches.length,
    );

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
    } catch (requestError) {
      setError(requestError.message || "Unable to generate matches.");
      setMatches([]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSendRequest = async (match) => {
    try {
      await sendMatchRequest(match.user_id);
      setRelationshipState((current) => ({ ...current, [match.user_id]: "pending" }));
    } catch (requestError) {
      setError(requestError.message || "Unable to send match request.");
    }
  };

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card className="overflow-hidden bg-ink text-white">
          <div className="space-y-6">
            <Badge tone="gold">AI Matchmaking</Badge>
            <div className="space-y-3">
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-white/55">
                Smart Discovery
              </p>
              <h1 className="max-w-2xl font-display text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                Find the strongest barter partners for your next growth sprint.
              </h1>
              <p className="max-w-2xl text-base leading-7 text-white/72">
                Our backend model weighs skill similarity, availability overlap, rating quality,
                and exchange history to rank the best introductions.
              </p>
            </div>
            <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
              <label className="space-y-2">
                <span className="text-sm font-semibold text-white/80">Skill you offer</span>
                <select
                  name="skill_offer"
                  value={formData.skill_offer}
                  onChange={handleChange}
                  disabled={isLoadingSkills}
                  className="w-full rounded-2xl border border-white/10 bg-white/95 px-4 py-3 text-sm text-slate-900 outline-none focus:ring-4 focus:ring-white/15"
                >
                  {skills.map((skill) => (
                    <option key={skill} value={skill}>
                      {skill}
                    </option>
                  ))}
                </select>
              </label>
              <label className="space-y-2">
                <span className="text-sm font-semibold text-white/80">Skill you want</span>
                <select
                  name="skill_want"
                  value={formData.skill_want}
                  onChange={handleChange}
                  disabled={isLoadingSkills}
                  className="w-full rounded-2xl border border-white/10 bg-white/95 px-4 py-3 text-sm text-slate-900 outline-none focus:ring-4 focus:ring-white/15"
                >
                  {skills.map((skill) => (
                    <option key={skill} value={skill}>
                      {skill}
                    </option>
                  ))}
                </select>
              </label>
              <div className="md:col-span-2 flex flex-col gap-3 sm:flex-row sm:items-center">
                <Button
                  type="submit"
                  className="bg-white text-ink hover:bg-slate-100"
                  disabled={isSubmitting || isLoadingSkills || skills.length < 2}
                >
                  {isLoadingSkills
                    ? "Loading skills..."
                    : isSubmitting
                      ? "Finding best matches..."
                      : "Generate top matches"}
                </Button>
                <p className="text-sm text-white/70">
                  Personalized with synthetic ML ranking and live scoring.
                </p>
              </div>
              {error ? <p className="md:col-span-2 text-sm font-medium text-rose-300">{error}</p> : null}
            </form>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-peach to-white">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
            Match Snapshot
          </p>
          {scoreSummary ? (
            <div className="mt-5 space-y-5">
              <div>
                <p className="font-display text-6xl font-semibold tracking-tight text-ink">
                  {scoreSummary.averageScore}%
                </p>
                <p className="mt-2 text-sm leading-7 text-slate-600">
                  Average fit across your top five recommendations.
                </p>
              </div>
              <div className="rounded-[1.5rem] bg-white/80 p-5">
                <p className="text-sm text-slate-500">Best current introduction</p>
                <p className="mt-2 font-display text-3xl font-semibold text-ink">
                  {scoreSummary.strongestMatch.name}
                </p>
                <p className="mt-1 text-sm text-slate-600">
                  Offers {scoreSummary.strongestMatch.skill} at {scoreSummary.strongestMatch.score}% predicted success.
                </p>
              </div>
            </div>
          ) : (
            <div className="mt-5 space-y-4">
              <p className="font-display text-4xl font-semibold tracking-tight text-ink">Ready to search</p>
              <p className="max-w-sm leading-7 text-slate-600">
                Choose your offer and learning goal to generate ranked barter partners from the AI pipeline.
              </p>
            </div>
          )}
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.34fr]">
        <div className="grid gap-6 md:grid-cols-2">
          {matches.length ? (
            matches.map((match, index) => (
              <Card
                key={match.name}
                className={index === 0 ? "bg-ink text-white" : "bg-white/90"}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-display text-2xl font-semibold">{match.name}</p>
                    <p className={`mt-2 text-sm ${index === 0 ? "text-white/70" : "text-slate-500"}`}>
                      Offers {match.skill}
                    </p>
                    <p className={`text-sm ${index === 0 ? "text-white/70" : "text-slate-500"}`}>
                      Great fit for learning {formData.skill_want}
                    </p>
                  </div>
                  <Badge tone={index === 0 ? "gold" : "mint"}>{match.score}% match</Badge>
                </div>
                <div className="mt-8 flex items-center justify-between">
                  <p className={`text-sm ${index === 0 ? "text-white/70" : "text-slate-500"}`}>
                    Exchange your {formData.skill_offer} expertise
                  </p>
                  {relationshipState[match.user_id] === "friend" ? (
                    <Button
                      as="link"
                      to="/chat"
                      variant={index === 0 ? "secondary" : "primary"}
                      className={index === 0 ? "bg-white text-ink" : ""}
                    >
                      Open chat
                    </Button>
                  ) : (
                    <Button
                      type="button"
                      onClick={() => handleSendRequest(match)}
                      disabled={relationshipState[match.user_id] === "pending"}
                      variant={index === 0 ? "secondary" : "primary"}
                      className={index === 0 ? "bg-white text-ink" : ""}
                    >
                      {relationshipState[match.user_id] === "incoming"
                        ? "Request waiting"
                        : relationshipState[match.user_id] === "pending"
                          ? "Request sent"
                          : "Send request"}
                    </Button>
                  )}
                </div>
              </Card>
            ))
          ) : (
            <Card className="md:col-span-2 bg-white/90">
              <p className="font-display text-3xl font-semibold tracking-tight text-ink">
                No matches yet
              </p>
              <p className="mt-3 max-w-xl leading-7 text-slate-600">
                Start with a skill pairing above and we&apos;ll generate five ranked recommendations from the backend model.
              </p>
            </Card>
          )}
        </div>

        <Card className="space-y-5 bg-gradient-to-br from-mint to-white">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Signals</p>
          <h2 className="font-display text-3xl font-semibold tracking-tight text-ink">
            What improves a match?
          </h2>
          <div className="space-y-4 text-sm leading-7 text-slate-600">
            <p>Skill alignment matters most, especially when each person wants what the other offers.</p>
            <p>Availability overlap and higher average ratings make intros more likely to convert.</p>
            <p>Prior exchange history helps the model favor reliable partners without dominating the ranking.</p>
            <p>
              Once a request is accepted, jump into the realtime chat experience from{" "}
              <Link to="/chat" className="font-semibold text-ink underline-offset-4 hover:underline">
                your social inbox
              </Link>
              .
            </p>
          </div>
        </Card>
      </section>
    </div>
  );
}
