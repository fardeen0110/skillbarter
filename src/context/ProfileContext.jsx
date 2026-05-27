import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";
import {
  fetchCurrentUser,
  getApiBaseUrl,
  updateProfile as updateProfileRequest,
  uploadProfileAvatar,
} from "../services/auth";

const ProfileContext = createContext(null);

function mapUserToProfile(user) {
  if (!user) {
    return null;
  }

  const avatarUrl = user.profile?.avatar_url || "";
  const normalizedAvatarUrl = avatarUrl
    ? /^https?:\/\//i.test(avatarUrl)
      ? avatarUrl
      : `${getApiBaseUrl()}${avatarUrl}`
    : "";

  return {
    name: user.name,
    email: user.email,
    bio: user.profile?.bio || "",
    city: user.profile?.city || "",
    availability: user.profile?.availability || "",
    experienceLevel: user.profile?.experience_level || "intermediate",
    profileImage: normalizedAvatarUrl,
    ratingAverage: user.profile?.rating_average || 0,
    ratingCount: user.profile?.rating_count || 0,
    skillsOffered: user.profile?.skills_offered || [],
    skillsWanted: user.profile?.skills_wanted || [],
    socialLinks: {
      linkedin: user.profile?.social_links?.linkedin || "",
      website: user.profile?.social_links?.website || "",
      x: user.profile?.social_links?.x || "",
    },
    followersCount: user.followers_count || 0,
    followingCount: user.following_count || 0,
    friendsCount: user.friends_count || 0,
    isAdmin: Boolean(user.is_admin),
    isVerified: Boolean(user.is_verified),
  };
}

export function ProfileProvider({ children }) {
  const { user, setUser } = useAuth();
  const [profile, setProfile] = useState(() => mapUserToProfile(user));
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setProfile(mapUserToProfile(user));
  }, [user]);

  const refreshProfile = useCallback(async () => {
    const nextUser = await fetchCurrentUser();
    setUser(nextUser);
    return mapUserToProfile(nextUser);
  }, [setUser]);

  const updateProfile = useCallback(
    async (payload) => {
      setIsSaving(true);
      try {
        const nextUser = await updateProfileRequest(payload);
        setUser(nextUser);
        const nextProfile = mapUserToProfile(nextUser);
        setProfile(nextProfile);
        return nextProfile;
      } finally {
        setIsSaving(false);
      }
    },
    [setUser],
  );

  const uploadAvatar = useCallback(
    async (file) => {
      setIsSaving(true);
      try {
        const nextUser = await uploadProfileAvatar(file);
        setUser(nextUser);
        const nextProfile = mapUserToProfile(nextUser);
        setProfile(nextProfile);
        return nextProfile;
      } finally {
        setIsSaving(false);
      }
    },
    [setUser],
  );

  const value = useMemo(
    () => ({
      profile,
      isSaving,
      refreshProfile,
      updateProfile,
      uploadAvatar,
    }),
    [isSaving, profile, refreshProfile, updateProfile, uploadAvatar],
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
