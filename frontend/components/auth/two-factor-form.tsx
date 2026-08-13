"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authService } from "../../services/auth";

interface TwoFactorFormProps {
  mode: "verify" | "enroll";
  onEnrollSuccess?: () => void;
}

export default function TwoFactorForm({ mode, onEnrollSuccess }: TwoFactorFormProps) {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  // Enrollment state
  const [factorId, setFactorId] = useState<string | null>(null);
  const [qrCodeSvg, setQrCodeSvg] = useState<string | null>(null);
  const [secretText, setSecretText] = useState<string | null>(null);

  // Load factors for verification, or enroll for enrollment
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      setError(null);
      try {
        if (mode === "verify") {
          // Find enrolled factors
          const factors = await authService.listFactors();
          const activeFactor = factors.totp[0];
          if (!activeFactor) {
            setError("No active 2FA factors found. Please contact support or enroll first.");
          } else {
            setFactorId(activeFactor.id);
          }
        } else if (mode === "enroll") {
          // Initialize enrollment
          const data = await authService.enrollTOTP("KHOJ Authenticator");
          setFactorId(data.id);
          if (data.totp) {
            setQrCodeSvg(data.totp.qr_code);
            setSecretText(data.totp.secret);
          }
        }
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Failed to initialize 2FA module.");
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [mode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!factorId) return;

    setLoading(true);
    setError(null);
    try {
      await authService.challengeAndVerifyTOTP(factorId, code);
      if (mode === "verify") {
        router.push("/dashboard");
      } else {
        setSuccess(true);
        if (onEnrollSuccess) onEnrollSuccess();
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Invalid authentication code. Please check your app and try again.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="w-full max-w-md p-8 bg-zinc-950/70 border border-zinc-800 rounded-2xl shadow-2xl backdrop-blur-xl text-center">
        <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-950/50 border border-emerald-500/30 text-emerald-400 mx-auto mb-4 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-zinc-100 mb-2">2FA Activated</h2>
        <p className="text-zinc-400 text-sm mb-6">
          Multi-Factor Authentication has been successfully configured. Your account is now protected with a 2FA layer.
        </p>
        <Link
          href="/dashboard"
          className="inline-block px-6 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/10 transition-all duration-200"
        >
          Go to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md p-8 bg-zinc-950/70 border border-zinc-800 rounded-2xl shadow-2xl backdrop-blur-xl transition-all duration-300 hover:border-zinc-700/80">
      <div className="flex flex-col items-center mb-6">
        <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-violet-950/50 border border-violet-500/30 text-violet-400 mb-4 shadow-[0_0_15px_rgba(139,92,246,0.15)]">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-zinc-100 tracking-tight">
          {mode === "verify" ? "Secure Verification" : "Enroll 2FA"}
        </h2>
        <p className="text-zinc-400 text-sm mt-1 text-center">
          {mode === "verify" ? "Provide authentication code" : "Set up Multi-Factor Authentication"}
        </p>
      </div>

      {error && (
        <div className="p-4 mb-6 rounded-lg bg-rose-950/30 border border-rose-500/20 text-rose-300 text-sm flex items-start gap-3">
          <svg className="w-5 h-5 shrink-0 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {mode === "enroll" && qrCodeSvg && (
        <div className="flex flex-col items-center mb-6">
          <div className="p-3 bg-white rounded-xl mb-4 shadow-[0_0_15px_rgba(255,255,255,0.1)] hover:scale-105 transition-transform duration-300">
            {/* Supabase returns raw SVG string, which we can safely render */}
            <div 
              className="w-40 h-40 flex items-center justify-center [&>svg]:w-full [&>svg]:h-full"
              dangerouslySetInnerHTML={{ __html: qrCodeSvg }} 
            />
          </div>
          <p className="text-zinc-400 text-xs text-center px-4 mb-3">
            Scan the QR code with your authenticator app (Google Authenticator, Duo, Authy).
          </p>
          {secretText && (
            <div className="w-full bg-zinc-900/60 border border-zinc-800 p-2.5 rounded-lg text-center flex flex-col items-center select-all">
              <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold mb-0.5">Secret Key</span>
              <span className="font-mono text-zinc-300 text-xs tracking-wider break-all">{secretText}</span>
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="code" className="block text-zinc-300 text-xs font-semibold uppercase tracking-wider mb-2">
            Verification Code
          </label>
          <input
            id="code"
            type="text"
            required
            disabled={loading || (mode === "verify" && !factorId)}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            className="w-full px-4 py-3 bg-zinc-900/60 border border-zinc-800 rounded-xl text-zinc-200 placeholder-zinc-500 text-center font-mono text-xl tracking-[0.5em] focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 disabled:opacity-50 transition-all duration-200"
            placeholder="000000"
            autoComplete="one-time-code"
            inputMode="numeric"
            pattern="[0-9]{6}"
          />
        </div>

        <button
          type="submit"
          disabled={loading || code.length < 6 || (mode === "verify" && !factorId)}
          className="w-full py-3 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/10 focus:outline-none disabled:opacity-50 transition-all duration-200 flex items-center justify-center gap-2"
        >
          {loading ? (
            <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            mode === "verify" ? "Confirm Code" : "Activate 2FA"
          )}
        </button>
      </form>

      {mode === "verify" && (
        <p className="text-zinc-500 text-xs text-center mt-6">
          Lost your device?{" "}
          <Link href="/login" className="text-violet-400 hover:text-violet-300 font-semibold hover:underline">
            Back to Sign In
          </Link>
        </p>
      )}
    </div>
  );
}
