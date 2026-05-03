import { motion } from "framer-motion";
import { AtSign, BriefcaseBusiness, Camera, Globe, MapPin, Save, Sparkles, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { Badge, SectionHeading } from "../components/Layout";
import { Button, Card, Input, Textarea } from "../components/ui";
import { useProfile } from "../context/ProfileContext";
import { useToast } from "../context/ToastContext";

function toCommaString(value) {
  return Array.isArray(value) ? value.join(", ") : "";
}

function fromCommaString(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function ProfilePage() {
  const { profile, updateProfile } = useProfile();
  const { pushToast } = useToast();
  const [formState, setFormState] = useState({
    name: "",
    bio: "",
    skillsOffered: "",
    skillsWanted: "",
    city: "",
    availability: "",
    profileImage: "",
    linkedin: "",
    website: "",
    x: "",
  });

  useEffect(() => {
    setFormState({
      name: profile?.name || "",
      bio: profile?.bio || "",
      skillsOffered: toCommaString(profile?.skillsOffered),
      skillsWanted: toCommaString(profile?.skillsWanted),
      city: profile?.city || "",
      availability: profile?.availability || "",
      profileImage: profile?.profileImage || "",
      linkedin: profile?.socialLinks?.linkedin || "",
      website: profile?.socialLinks?.website || "",
      x: profile?.socialLinks?.x || "",
    });
  }, [profile]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    updateProfile({
      name: formState.name.trim() || profile.name,
      bio: formState.bio.trim(),
      skillsOffered: fromCommaString(formState.skillsOffered),
      skillsWanted: fromCommaString(formState.skillsWanted),
      city: formState.city.trim(),
      availability: formState.availability.trim(),
      profileImage: formState.profileImage.trim(),
      socialLinks: {
        linkedin: formState.linkedin.trim(),
        website: formState.website.trim(),
        x: formState.x.trim(),
      },
    });

    pushToast({
      title: "Profile updated",
      message: "Your frontend profile details have been refreshed.",
      tone: "success",
    });
  };

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
        <Card className="overflow-hidden bg-slate-950 text-white shadow-float dark:bg-slate-900">
          <div className="absolute inset-0 bg-spotlight opacity-70" />
          <div className="relative space-y-6">
            <Badge tone="mint">Profile studio</Badge>
            <div>
              <h1 className="max-w-2xl font-display text-4xl font-semibold tracking-tight sm:text-5xl">
                Build a profile that makes the right people want to reply.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-white/70">
                Shape your positioning, skill tags, and social proof so matchmaking and chat feel more intentional.
              </p>
            </div>

            <div className="rounded-[1.75rem] border border-white/10 bg-white/8 p-5 backdrop-blur-sm">
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-white/55">Current identity</p>
              <div className="mt-4 flex items-center gap-4">
                {formState.profileImage ? (
                  <img src={formState.profileImage} alt={formState.name} className="h-16 w-16 rounded-3xl object-cover" />
                ) : (
                  <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-white/12">
                    <UserRound className="h-7 w-7 text-white/75" />
                  </div>
                )}
                <div>
                  <p className="text-lg font-semibold text-white">{formState.name || "Your name"}</p>
                  <p className="text-sm text-white/65">{profile?.email}</p>
                  <p className="mt-2 text-sm text-white/55">{formState.city || "City not set yet"}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <SectionHeading
            eyebrow="Editable profile"
            title="Refine how you show up in the network"
            body="This editor keeps your existing backend auth untouched and enhances the frontend-facing profile experience."
          />

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <div className="grid gap-5 md:grid-cols-2">
              <Input
                label="Name"
                name="name"
                value={formState.name}
                onChange={handleChange}
                placeholder="Your full name"
                icon={UserRound}
              />
              <Input
                label="City"
                name="city"
                value={formState.city}
                onChange={handleChange}
                placeholder="Bengaluru"
                icon={MapPin}
              />
            </div>

            <Textarea
              label="Bio"
              name="bio"
              value={formState.bio}
              onChange={handleChange}
              placeholder="What do you do, what do you teach well, and what kind of people do you want to meet?"
              helper="Keep it sharp, credible, and easy to scan."
            />

            <div className="grid gap-5 md:grid-cols-2">
              <Textarea
                label="Skills offered"
                name="skillsOffered"
                value={formState.skillsOffered}
                onChange={handleChange}
                placeholder="React, Product Strategy, Public Speaking"
                helper="Separate each skill with a comma."
              />
              <Textarea
                label="Skills wanted"
                name="skillsWanted"
                value={formState.skillsWanted}
                onChange={handleChange}
                placeholder="AI Workflow Design, Growth Marketing"
                helper="Separate each skill with a comma."
              />
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <Input
                label="Availability"
                name="availability"
                value={formState.availability}
                onChange={handleChange}
                placeholder="Weeknights and Saturdays"
                icon={Sparkles}
              />
              <Input
                label="Profile image URL"
                name="profileImage"
                value={formState.profileImage}
                onChange={handleChange}
                placeholder="https://..."
                icon={Camera}
              />
            </div>

            <div className="grid gap-5 md:grid-cols-3">
              <Input
                label="LinkedIn"
                name="linkedin"
                value={formState.linkedin}
                onChange={handleChange}
                placeholder="https://linkedin.com/in/..."
                icon={BriefcaseBusiness}
              />
              <Input
                label="Website"
                name="website"
                value={formState.website}
                onChange={handleChange}
                placeholder="https://your-site.com"
                icon={Globe}
              />
              <Input
                label="X / Twitter"
                name="x"
                value={formState.x}
                onChange={handleChange}
                placeholder="https://x.com/..."
                icon={AtSign}
              />
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                These profile details are preserved in the frontend experience and do not change backend auth APIs.
              </p>
              <Button type="submit" icon={Save}>
                Save profile
              </Button>
            </div>
          </form>
        </Card>
      </section>

      <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="grid gap-6 md:grid-cols-3">
          {[
            { label: "Credibility", value: "High", note: "Clear skills and city improve trust." },
            { label: "Discoverability", value: "Strong", note: "More skill tags increase profile matches." },
            { label: "Conversation fit", value: "Better", note: "Availability helps requests convert faster." },
          ].map((item) => (
            <div key={item.label} className="rounded-[1.5rem] bg-slate-50/80 p-5 dark:bg-slate-900/70">
              <p className="text-sm text-slate-500 dark:text-slate-400">{item.label}</p>
              <p className="mt-3 font-display text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">
                {item.value}
              </p>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{item.note}</p>
            </div>
          ))}
        </Card>
      </motion.section>
    </div>
  );
}
