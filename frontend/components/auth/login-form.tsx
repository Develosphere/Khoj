"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authService } from "../../services/auth";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await authService.signIn({ email, password });
      
      // Check if MFA is required
      const assurance = await authService.getAssuranceLevel();
      const factors = await authService.listFactors();
      const mfaRequired = 
        assurance.nextLevel === "aal2" && 
        assurance.currentLevel !== "aal2" && 
        factors.totp.length > 0;

      if (mfaRequired) {
        // Redirect to 2FA verification page
        router.push("/verify-2fa");
      } else {
        // Go to dashboard
        router.push("/dashboard");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to sign in. Please verify your credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError(null);
    try {
      await authService.signInWithGoogle();
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to initialize Google Sign-In.");
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md p-8 bg-zinc-950/70 border border-zinc-800 rounded-2xl shadow-2xl backdrop-blur-xl transition-all duration-300 hover:border-zinc-700/80">
      <div className="flex flex-col items-center mb-8">
        <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-violet-950/50 border border-violet-500/30 text-violet-400 mb-4 shadow-[0_0_15px_rgba(139,92,246,0.15)]">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-zinc-100 tracking-tight">Access KHOJ</h2>
        <p className="text-zinc-400 text-sm mt-1 text-center">AI Investigation & 3D Reconstruction Platform</p>
      </div>

      {error && (
        <div className="p-4 mb-6 rounded-lg bg-rose-950/30 border border-rose-500/20 text-rose-300 text-sm flex items-start gap-3">
          <svg className="w-5 h-5 shrink-0 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="email" className="block text-zinc-300 text-xs font-semibold uppercase tracking-wider mb-2">
            Email Address
          </label>
          <input
            id="email"
            type="email"
            required
            disabled={loading}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 bg-zinc-900/60 border border-zinc-800 rounded-xl text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 disabled:opacity-50 transition-all duration-200"
            placeholder="investigator@khoj.agency"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-zinc-300 text-xs font-semibold uppercase tracking-wider mb-2">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            disabled={loading}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 bg-zinc-900/60 border border-zinc-800 rounded-xl text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 disabled:opacity-50 transition-all duration-200"
            placeholder="••••••••••••"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/10 focus:outline-none disabled:opacity-50 transition-all duration-200 flex items-center justify-center gap-2"
        >
          {loading ? (
            <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            "Authenticate"
          )}
        </button>
      </form>

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-zinc-800"></div>
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="px-3 bg-zinc-950/70 text-zinc-500 backdrop-blur-xl">Or continue with</span>
        </div>
      </div>

      <button
        onClick={handleGoogleSignIn}
        type="button"
        disabled={loading}
        className="w-full py-3 px-4 bg-zinc-900/40 hover:bg-zinc-900/80 border border-zinc-800 hover:border-zinc-700/80 text-zinc-300 font-medium rounded-xl transition-all duration-200 flex items-center justify-center gap-3 disabled:opacity-50"
      >
        <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" width="24" height="24">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.85z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.85c.87-2.6 3.3-4.53 6.16-4.53z"
          />
        </svg>
        <span>Google Workspaces</span>
      </button>

      <p className="text-zinc-500 text-xs text-center mt-6">
        Don't have credentials?{" "}
        <Link href="/signup" className="text-violet-400 hover:text-violet-300 font-semibold hover:underline">
          Register account
        </Link>
      </p>
    </div>
  );
}
