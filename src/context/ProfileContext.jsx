import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";

const STORAGE_KEY = "skillbarter_profile";
const ProfileContext = createContext(null);

const defaultProfile = {
  bio: "Product-minded member focused on high-leverage skill swaps and consistent learning.",
  skillsOffered: ["React", "Product Strategy", "Public Speaking"],
  skillsWanted: ["AI Workflow Design", "Growth Marketing", "Brand Storytelling"],
  city: "Bengaluru",
  availability: "Weeknights and Saturdays",
  profileImage: "",
  socialLinks: {
    linkedin: "",
    website: "",
    x: "",
  },
};

function readStoredProfile() {
  if (typeof window === "undefined") {
    return null;
  }

  const value = window.localStorage.getItem(STORAGE_KEY);
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function ProfileProvider({ children }) {
  const { user } = useAuth();
  const [profile, setProfile] = useState(() => {
    const stored = readStoredProfile();
    return {
      ...defaultProfile,
      ...stored,
      name: stored?.name || "",
      email: stored?.email || "",
      socialLinks: {
        ...defaultProfile.socialLinks,
        ...stored?.socialLinks,
      },
    };
  });

  useEffect(() => {
    if (!user) {
      return;
    }

    setProfile((current) => {
      const nextProfile = {
        ...defaultProfile,
        ...current,
        name: current.name || user.name,
        email: user.email,
        socialLinks: {
          ...defaultProfile.socialLinks,
          ...current.socialLinks,
        },
      };

      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextProfile));
      return nextProfile;
    });
  }, [user]);

  const value = useMemo(
    () => ({
      profile,
      updateProfile(updates) {
        setProfile((current) => {
          const nextProfile = {
            ...current,
            ...updates,
            socialLinks: {
              ...current.socialLinks,
              ...updates.socialLinks,
            },
          };
          window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextProfile));
          return nextProfile;
        });
      },
    }),
    [profile],
  );

  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}

export function useProfile() {
  const context = useContext(ProfileContext);

  if (!context) {
    throw new Error("useProfile must be used within a ProfileProvider");
  }

  return context;
}
