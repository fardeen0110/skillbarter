import { motion } from "framer-motion";
import { AtSign, BriefcaseBusiness, Camera, Globe, MapPin, Save, Sparkles, Upload, UserRound } from "lucide-react";
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
  const { profile, updateProfile, uploadAvatar, isSaving } = useProfile();
  const { pushToast } = useToast();
  const [selectedFile, setSelectedFile] = useState(null);
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
      experienceLevel: profile?.experienceLevel || "intermediate",
      linkedin: profile?.socialLinks?.linkedin || "",
      website: profile?.socialLinks?.website || "",
      x: profile?.socialLinks?.x || "",
    });
  }, [profile]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      await updateProfile({
        name: formState.name.trim() || profile.name,
        bio: formState.bio.trim(),
        city: formState.city.trim(),
        availability: formState.availability.trim(),
        experience_level: formState.experienceLevel,
        linkedin: formState.linkedin.trim(),
        website: formState.website.trim(),
        x: formState.x.trim(),
        skills_offered: fromCommaString(formState.skillsOffered),
        skills_wanted: fromCommaString(formState.skillsWanted),
      });

      if (selectedFile) {
        await uploadAvatar(selectedFile);
        setSelectedFile(null);
      }

      pushToast({
        title: "Profile updated",
        message: "Your profile is now persisted to the database.",
        tone: "success",
      });
    } catch (error) {
      pushToast({
        title: "Update failed",
        message: error.message || "Unable to save your profile.",
        tone: "error",
      });
    }
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
                {profile?.profileImage ? (
                  <img src={profile.profileImage} alt={formState.name} className="h-16 w-16 rounded-3xl object-cover" />
                ) : (
                  <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-white/12">
                    <UserRound className="h-7 w-7 text-white/75" />
                  </div>
                )}
                <div>
                  <p className="text-lg font-semibold text-white">{formState.name || "Your name"}</p>
                  <p className="text-sm text-white/65">{profile?.email}</p>
                  <p className="mt-2 text-sm text-white/55">{formState.city || "City not set yet"}</p>
                  <p className="mt-1 text-xs uppercase tracking-[0.2em] text-white/45">
                    {profile?.ratingAverage ? `${profile.ratingAverage}/5 from ${profile.ratingCount} reviews` : "No reviews yet"}
                  </p>
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
              <label className="block space-y-2">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">Avatar upload</span>
                <label className="flex cursor-pointer items-center gap-3 rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-950/80 dark:text-slate-300">
                  <Camera className="h-4 w-4" />
                  <span>{selectedFile?.name || "Choose JPEG, PNG, or WEBP under 2.5MB"}</span>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    className="hidden"
                    onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
                  />
                </label>
              </label>
            </div>

            <div className="grid gap-5 md:grid-cols-2">
              <label className="block space-y-2">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">Experience level</span>
                <select
                  name="experienceLevel"
                  value={formState.experienceLevel}
                  onChange={handleChange}
                  className="w-full rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-primary/40 focus:ring-4 focus:ring-primary/10 dark:border-slate-800 dark:bg-slate-950/80 dark:text-white"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="expert">Expert</option>
                </select>
              </label>
              <div className="rounded-[1.5rem] bg-slate-50/80 p-5 dark:bg-slate-900/70">
                <p className="text-sm text-slate-500 dark:text-slate-400">Network stats</p>
                <p className="mt-3 font-display text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">
                  {profile?.friendsCount || 0} connections
                </p>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  {profile?.followersCount || 0} followers and {profile?.followingCount || 0} following.
                </p>
              </div>
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
              <Button type="submit" icon={selectedFile ? Upload : Save} isLoading={isSaving}>
                {isSaving ? "Saving profile" : "Save profile"}
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
