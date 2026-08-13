"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../hooks/useAuth";

export default function HomePage() {
  const { user, loading, mfaRequired } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (user) {
        if (mfaRequired) {
          router.push("/verify-2fa");
        } else {
          router.push("/dashboard");
        }
      } else {
        router.push("/login");
      }
    }
  }, [user, loading, mfaRequired, router]);

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-black text-zinc-300">
      <div className="flex flex-col items-center gap-4">
        <svg className="animate-spin h-10 w-10 text-violet-500" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <span className="text-zinc-500 font-medium tracking-wider text-sm uppercase">Loading KHOJ Core...</span>
      </div>
    </main>
  );
}
