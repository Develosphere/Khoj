"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../../hooks/useAuth";
import { authService } from "../../services/auth";
import { apiService, DashboardStats } from "../../services/api";
import TwoFactorForm from "../../components/auth/two-factor-form";

interface CaseItem {
  id: string;
  title: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export default function DashboardPage() {
  const { user, loading: authLoading, mfaLevel, mfaRequired, refreshState: refreshAuth } = useAuth();
  const router = useRouter();

  // Page states
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    total_cases: 0,
    active_cases: 0,
    total_sources: 0,
    total_evidence: 0,
    total_theories: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form states for new case modal
  const [showModal, setShowModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [modalLoading, setModalLoading] = useState(false);

  // Account settings visibility
  const [showEnrollMfa, setShowEnrollMfa] = useState(false);
  const [securityActionLoading, setSecurityActionLoading] = useState(false);

  // Fetch all cases & stats from the API
  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [casesData, statsData] = await Promise.all([
        apiService.getCases(),
        apiService.getDashboardStats(),
      ]);
      setCases(casesData || []);
      setStats(statsData || {
        total_cases: 0,
        active_cases: 0,
        total_sources: 0,
        total_evidence: 0,
        total_theories: 0,
      });
    } catch (err: any) {
      console.error("Error fetching dashboard data:", err);
      setError(err.message || "Failed to load investigations data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        router.push("/login");
      } else if (mfaRequired) {
        router.push("/verify-2fa");
      } else {
        fetchDashboardData();
      }
    }
  }, [user, authLoading, mfaRequired, router, fetchDashboardData]);

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    setModalLoading(true);
    setError(null);
    try {
      await apiService.createCase({
        title: newTitle,
        description: newDescription,
      });
      setNewTitle("");
      setNewDescription("");
      setShowModal(false);
      await fetchDashboardData();
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to create investigation case.");
    } finally {
      setModalLoading(false);
    }
  };

  const handleDeleteCase = async (caseId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // prevent card click mapping
    if (!confirm("Are you sure you want to delete this case? All extracted sources, evidence, and theories will be lost permanently.")) {
      return;
    }
    try {
      await apiService.deleteCase(caseId);
      await fetchDashboardData();
    } catch (err: any) {
      console.error(err);
      alert(err.message || "Failed to delete case.");
    }
  };

  const handleToggleStatus = async (caseId: string, currentStatus: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const nextStatus = currentStatus === "active" ? "archived" : "active";
    try {
      await apiService.updateCase(caseId, { status: nextStatus });
      await fetchDashboardData();
    } catch (err: any) {
      console.error(err);
      alert(err.message || "Failed to update case status.");
    }
  };

  const handleSignOut = async () => {
    try {
      await authService.signOut();
      router.push("/login");
    } catch (err: any) {
      console.error(err);
      alert("Error signing out");
    }
  };

  const handleDisableMfa = async () => {
    if (!confirm("Are you sure you want to disable 2FA? This will reduce your account security.")) {
      return;
    }
    setSecurityActionLoading(true);
    setError(null);
    try {
      const factors = await authService.listFactors();
      for (const factor of factors.all) {
        await authService.unenrollFactor(factor.id);
      }
      await refreshAuth();
      setShowEnrollMfa(false);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to disable 2FA.");
    } finally {
      setSecurityActionLoading(false);
    }
  };

  if (authLoading || !user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-black text-zinc-400">
        <svg className="animate-spin h-8 w-8 text-violet-500 mb-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <span>Verifying clearance level...</span>
      </div>
    );
  }

  const fullName = user.user_metadata?.full_name || "Investigator";

  return (
    <div className="min-h-screen bg-black text-zinc-100 font-sans relative overflow-hidden flex flex-col">
      {/* Background glow effects */}
      <div className="absolute w-[800px] h-[800px] rounded-full bg-violet-600/5 blur-[150px] top-[-200px] right-[-200px] pointer-events-none"></div>
      <div className="absolute w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] bottom-[-200px] left-[-200px] pointer-events-none"></div>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_50%_-10%,rgba(139,92,246,0.03),rgba(255,255,255,0))] pointer-events-none"></div>

      {/* Header Area */}
      <header className="border-b border-zinc-800 bg-zinc-950/40 backdrop-blur-md relative z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-violet-950/80 border border-violet-500/30 flex items-center justify-center text-violet-400 font-bold shadow-[0_0_10px_rgba(139,92,246,0.15)]">
              K
            </div>
            <span className="font-bold text-lg tracking-wider bg-gradient-to-r from-zinc-100 to-zinc-400 bg-clip-text text-transparent">
              KHOJ PLATFORM
            </span>
          </div>

          <div className="flex items-center gap-4">
            <Link href="/scrapers" className="text-zinc-400 hover:text-zinc-200 text-xs font-mono tracking-wider uppercase transition-all duration-200 mr-2 border border-zinc-800 bg-zinc-900/50 hover:bg-zinc-800/80 px-3 py-1.5 rounded-lg">
              Scraper Tool
            </Link>
            <span className="text-zinc-500 text-xs font-mono hidden md:inline uppercase">
              Clearance: AAL-{mfaLevel === "aal2" ? "2 (SECURE)" : "1 (STANDARD)"}
            </span>
            <button
              onClick={handleSignOut}
              className="px-4 py-2 bg-zinc-900 border border-zinc-800 hover:border-zinc-700/80 hover:bg-zinc-800/60 rounded-xl text-zinc-300 text-sm font-medium transition-all duration-200"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10 relative z-10">
        {/* Welcome Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-zinc-100">Welcome, {fullName}</h1>
            <p className="text-zinc-400 text-sm mt-1">Manage cases, analyze sources, and generate 3D simulations.</p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="px-5 py-3 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-indigo-500/10 transition-all duration-200 flex items-center gap-2 self-start md:self-auto"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            New Investigation
          </button>
        </div>

        {error && (
          <div className="p-4 mb-8 rounded-lg bg-rose-950/30 border border-rose-500/20 text-rose-300 text-sm flex items-start gap-3">
            <svg className="w-5 h-5 shrink-0 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* Dashboard Stats */}
        <section className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-10">
          <div className="p-5 bg-zinc-950/40 border border-zinc-900 rounded-xl">
            <span className="text-zinc-500 text-xs font-semibold uppercase tracking-wider block">Investigations</span>
            <span className="text-2xl font-bold text-zinc-100 block mt-1">{stats.total_cases}</span>
          </div>
          <div className="p-5 bg-zinc-950/40 border border-zinc-900 rounded-xl">
            <span className="text-zinc-500 text-xs font-semibold uppercase tracking-wider block">Active Cases</span>
            <span className="text-2xl font-bold text-zinc-100 block mt-1">{stats.active_cases}</span>
          </div>
          <div className="p-5 bg-zinc-950/40 border border-zinc-900 rounded-xl">
            <span className="text-zinc-500 text-xs font-semibold uppercase tracking-wider block">Sources Extracted</span>
            <span className="text-2xl font-bold text-zinc-100 block mt-1">{stats.total_sources}</span>
          </div>
          <div className="p-5 bg-zinc-950/40 border border-zinc-900 rounded-xl">
            <span className="text-zinc-500 text-xs font-semibold uppercase tracking-wider block">Evidence Claims</span>
            <span className="text-2xl font-bold text-zinc-100 block mt-1">{stats.total_evidence}</span>
          </div>
          <div className="p-5 bg-zinc-950/40 border border-zinc-900 rounded-xl col-span-2 lg:col-span-1">
            <span className="text-zinc-500 text-xs font-semibold uppercase tracking-wider block">Generated Theories</span>
            <span className="text-2xl font-bold text-zinc-100 block mt-1">{stats.total_theories}</span>
          </div>
        </section>

        {/* Investigations List */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-zinc-200 mb-6 flex items-center gap-2">
            <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Investigations List
          </h2>

          {loading ? (
            <div className="py-20 text-center flex flex-col items-center gap-3">
              <svg className="animate-spin h-7 w-7 text-zinc-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-zinc-500 text-sm">Querying active database index...</span>
            </div>
          ) : cases.length === 0 ? (
            <div className="border border-dashed border-zinc-800 p-12 text-center rounded-2xl bg-zinc-950/20 backdrop-blur-xl">
              <svg className="w-12 h-12 text-zinc-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-zinc-300 font-semibold mb-1">No Active Cases Found</h3>
              <p className="text-zinc-500 text-sm mb-6 max-w-sm mx-auto">
                Start a new investigation to begin collecting web sources, analyzing evidence, and creating 3D reconstructions.
              </p>
              <button
                onClick={() => setShowModal(true)}
                className="px-4 py-2.5 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-300 font-medium rounded-xl text-sm transition-all duration-200"
              >
                Create First Case
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {cases.map((c) => (
                <div
                  key={c.id}
                  onClick={() => router.push(`/investigations/${c.id}`)}
                  className="group relative p-6 bg-zinc-950/40 border border-zinc-900 hover:border-zinc-800/80 rounded-2xl shadow-xl hover:shadow-[0_0_20px_rgba(139,92,246,0.03)] cursor-pointer flex flex-col justify-between transition-all duration-300"
                >
                  <div>
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <h3 className="font-bold text-zinc-100 tracking-wide line-clamp-1 group-hover:text-violet-400 transition-colors duration-200">
                        {c.title}
                      </h3>
                      {c.status === "archived" ? (
                        <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-500 text-[10px] font-mono uppercase tracking-wider">
                          Archived
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-emerald-950/30 border border-emerald-500/20 text-emerald-400 text-[10px] font-mono uppercase tracking-wider shadow-[0_0_8px_rgba(16,185,129,0.05)]">
                          Active
                        </span>
                      )}
                    </div>
                    <p className="text-zinc-400 text-xs leading-relaxed line-clamp-3 mb-6">
                      {c.description || "No description provided. Click to open and begin gathering details."}
                    </p>
                  </div>

                  <div className="flex items-center justify-between border-t border-zinc-900/60 pt-4 mt-auto">
                    <span className="text-zinc-500 font-mono text-[10px] uppercase">
                      Updated: {new Date(c.updated_at).toLocaleDateString()}
                    </span>
                    <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <button
                        onClick={(e) => handleToggleStatus(c.id, c.status, e)}
                        title={c.status === "active" ? "Archive Case" : "Activate Case"}
                        className="p-2 rounded-lg bg-zinc-900/60 border border-zinc-800/60 hover:bg-zinc-900 hover:border-zinc-700/80 text-zinc-400 hover:text-zinc-200 transition-all duration-200"
                      >
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          {c.status === "active" ? (
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                          ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          )}
                        </svg>
                      </button>
                      <button
                        onClick={(e) => handleDeleteCase(c.id, e)}
                        title="Delete Case"
                        className="p-2 rounded-lg bg-zinc-900/60 border border-zinc-800/60 hover:bg-rose-950/40 hover:border-rose-500/30 text-zinc-400 hover:text-rose-400 transition-all duration-200"
                      >
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Security & 2FA Panel */}
        <section className="p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl shadow-xl">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-bold text-zinc-200 flex items-center gap-2">
                <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Account Security Settings
              </h3>
              <p className="text-zinc-400 text-xs mt-1 max-w-xl leading-relaxed">
                Add an extra layer of defense. With Multi-Factor Authentication enabled, you will be prompted for a 2FA OTP code whenever you authenticate.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-zinc-400 text-xs font-semibold uppercase tracking-wider block">
                Status:{" "}
                {mfaLevel === "aal2" ? (
                  <span className="text-emerald-400">Secure (MFA)</span>
                ) : (
                  <span className="text-amber-400">Basic (1FA)</span>
                )}
              </span>
              {mfaLevel === "aal2" ? (
                <button
                  onClick={handleDisableMfa}
                  disabled={securityActionLoading}
                  className="px-4 py-2 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-500/30 text-rose-300 text-xs font-bold rounded-xl transition-all duration-200"
                >
                  Disable 2FA
                </button>
              ) : (
                !showEnrollMfa && (
                  <button
                    onClick={() => setShowEnrollMfa(true)}
                    className="px-4 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl shadow-lg transition-all duration-200"
                  >
                    Set Up 2FA
                  </button>
                )
              )}
            </div>
          </div>

          {showEnrollMfa && mfaLevel !== "aal2" && (
            <div className="relative mt-8 p-6 bg-zinc-950/60 border border-zinc-900 rounded-2xl flex flex-col items-center">
              <button
                onClick={() => setShowEnrollMfa(false)}
                className="absolute top-4 right-4 text-zinc-500 hover:text-zinc-300 transition-colors duration-200"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              <div className="w-full max-w-sm">
                <TwoFactorForm mode="enroll" onEnrollSuccess={async () => {
                  await refreshAuth();
                  await fetchDashboardData();
                }} />
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Creation Modal Overlay */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md transition-opacity duration-300">
          <div className="w-full max-w-md p-8 bg-zinc-950/80 border border-zinc-800 rounded-2xl shadow-2xl relative">
            <button
              onClick={() => {
                setShowModal(false);
                setNewTitle("");
                setNewDescription("");
              }}
              className="absolute top-4 right-4 text-zinc-500 hover:text-zinc-300 transition-colors duration-200"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div className="flex flex-col items-center mb-6">
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-violet-950/50 border border-violet-500/30 text-violet-400 mb-4 shadow-[0_0_15px_rgba(139,92,246,0.15)]">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-zinc-100 tracking-tight">Start Investigation</h2>
              <p className="text-zinc-500 text-xs mt-1 text-center">Define parameters for a new investigation case</p>
            </div>

            <form onSubmit={handleCreateCase} className="space-y-5">
              <div>
                <label htmlFor="title" className="block text-zinc-300 text-xs font-semibold uppercase tracking-wider mb-2">
                  Case Title
                </label>
                <input
                  id="title"
                  type="text"
                  required
                  disabled={modalLoading}
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-900/60 border border-zinc-800 rounded-xl text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 disabled:opacity-50 transition-all duration-200"
                  placeholder="e.g. Incident at Grid Sector 7"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-zinc-300 text-xs font-semibold uppercase tracking-wider mb-2">
                  Case Description
                </label>
                <textarea
                  id="description"
                  rows={3}
                  disabled={modalLoading}
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-900/60 border border-zinc-800 rounded-xl text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 disabled:opacity-50 transition-all duration-200 resize-none"
                  placeholder="Describe context, initial reports, key facts, coordinates..."
                />
              </div>

              <button
                type="submit"
                disabled={modalLoading || !newTitle.trim()}
                className="w-full py-3 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/10 focus:outline-none disabled:opacity-50 transition-all duration-200 flex items-center justify-center gap-2"
              >
                {modalLoading ? (
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : (
                  "Create Case File"
                )}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
