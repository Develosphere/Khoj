"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../../hooks/useAuth";
import { apiService } from "../../services/api";

interface CaseItem {
  id: string;
  title: string;
}

interface ScrapedSource {
  title: string;
  url: string;
  source_name: string;
  published_at?: string;
  content: string;
}

export default function ScrapersPage() {
  const { user, loading: authLoading, mfaRequired } = useAuth();
  const router = useRouter();

  // Data states
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [query, setQuery] = useState("Ukraine conflict");
  const [sources, setSources] = useState<ScrapedSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [casesLoading, setCasesLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importingStates, setImportingStates] = useState<Record<number, boolean>>({});
  const [selectedCaseIds, setSelectedCaseIds] = useState<Record<number, string>>({});
  const [importSuccess, setImportSuccess] = useState<string | null>(null);

  // Fetch investigator's cases for the selector
  const fetchCases = useCallback(async () => {
    setCasesLoading(true);
    try {
      const data = await apiService.getCases();
      setCases(data || []);
      // Pre-select first case if exists
      if (data && data.length > 0) {
        const initialSelections: Record<number, string> = {};
        // Fill initial selections
        setSelectedCaseIds(initialSelections);
      }
    } catch (err: any) {
      console.error("Failed to load cases", err);
      setError("Could not retrieve active case files. Create a case first.");
    } finally {
      setCasesLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        router.push("/login");
      } else if (mfaRequired) {
        router.push("/verify-2fa");
      } else {
        fetchCases();
      }
    }
  }, [user, authLoading, mfaRequired, router, fetchCases]);

  // Execute scrape operation
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setSources([]);
    setImportSuccess(null);

    try {
      const result = await apiService.searchSources(query);
      setSources(result.sources || []);
      if (!result.sources || result.sources.length === 0) {
        setError("No news articles found for this query. Try adjusting keywords.");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to fetch articles from scraping service.");
    } finally {
      setLoading(false);
    }
  };

  // Import source to selected case
  const handleImport = async (idx: number, source: ScrapedSource) => {
    const caseId = selectedCaseIds[idx];
    if (!caseId) {
      alert("Please select a target case file to link this source.");
      return;
    }

    setImportingStates((prev) => ({ ...prev, [idx]: true }));
    setImportSuccess(null);

    try {
      await apiService.addSourceToCase(caseId, {
        title: source.title,
        url: source.url,
        source_name: source.source_name,
        published_at: source.published_at || null,
        content: source.content,
      });

      const selectedCase = cases.find((c) => c.id === caseId);
      setImportSuccess(`Successfully imported "${source.title.slice(0, 30)}..." into case: ${selectedCase?.title}`);
      
      // Auto clear success notice after 4 seconds
      setTimeout(() => setImportSuccess(null), 4000);
    } catch (err: any) {
      console.error(err);
      alert(err.message || "Failed to link source to case file.");
    } finally {
      setImportingStates((prev) => ({ ...prev, [idx]: false }));
    }
  };

  if (authLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-black text-zinc-400">
        <svg className="animate-spin h-8 w-8 text-violet-500 mb-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <span>Verifying credentials...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-zinc-100 font-sans flex flex-col relative overflow-hidden">
      {/* Decorative gradient glow */}
      <div className="absolute w-[800px] h-[800px] rounded-full bg-violet-600/5 blur-[150px] top-[-200px] right-[-200px] pointer-events-none"></div>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_50%_-10%,rgba(139,92,246,0.02),rgba(255,255,255,0))] pointer-events-none"></div>

      {/* Header bar */}
      <header className="border-b border-zinc-900 bg-zinc-950/40 backdrop-blur-md relative z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200 transition-all duration-200">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <span className="font-bold text-sm text-zinc-300 tracking-wide uppercase">Source Scraper Tool</span>
          </div>
          <Link href="/dashboard" className="text-zinc-500 hover:text-zinc-300 text-xs font-mono tracking-wider uppercase transition-colors duration-200">
            Go to Case Board
          </Link>
        </div>
      </header>

      {/* Main layout */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-10 relative z-10 flex flex-col">
        <div className="mb-10 text-center max-w-xl mx-auto">
          <h1 className="text-3xl font-extrabold tracking-tight text-zinc-100">Live News Scraper</h1>
          <p className="text-zinc-400 text-sm mt-2">Scrape recent web articles and official feeds globally, and link chosen elements directly to open case files.</p>
        </div>

        {/* Search Console */}
        <section className="mb-10 max-w-2xl w-full mx-auto">
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              required
              disabled={loading}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 px-5 py-3.5 bg-zinc-950/60 border border-zinc-800 rounded-xl text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all duration-200"
              placeholder="e.g. Ukraine grid cybersecurity"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-6 py-3.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:opacity-50 text-white font-semibold text-sm rounded-xl shadow-lg transition-all duration-200 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Scraping...
                </>
              ) : (
                "Search & Scrape"
              )}
            </button>
          </form>
        </section>

        {/* Notices */}
        {error && (
          <div className="p-4 mb-8 rounded-lg bg-rose-950/20 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2 max-w-2xl mx-auto w-full">
            <svg className="w-5 h-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {importSuccess && (
          <div className="p-4 mb-8 rounded-lg bg-emerald-950/30 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2 max-w-2xl mx-auto w-full shadow-[0_0_10px_rgba(16,185,129,0.05)]">
            <svg className="w-5 h-5 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{importSuccess}</span>
          </div>
        )}

        {/* Results view */}
        <section className="flex-1">
          {loading ? (
            <div className="py-20 text-center flex flex-col items-center justify-center gap-3">
              <svg className="animate-spin h-7 w-7 text-zinc-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-zinc-500 text-sm">Querying Google News RSS indices and scraping details...</span>
            </div>
          ) : sources.length === 0 ? (
            <div className="border border-zinc-900 bg-zinc-950/20 p-12 text-center rounded-2xl max-w-md mx-auto">
              <svg className="w-12 h-12 text-zinc-700 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <h3 className="text-zinc-300 font-semibold mb-1">No Scraped Results</h3>
              <p className="text-zinc-500 text-xs leading-relaxed">
                Enter an incident keywords query above to collect news, reports, and public feeds dynamically.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-3 mb-6">
                <span className="text-xs font-mono text-zinc-500">COLLECTED ARTICLES: {sources.length}</span>
              </div>

              {sources.map((src, idx) => (
                <div
                  key={idx}
                  className="p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl hover:border-zinc-800 transition-all duration-200 flex flex-col md:flex-row gap-6 justify-between items-start md:items-center"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="px-2.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 font-mono text-[9px] uppercase tracking-wider">
                        {src.source_name}
                      </span>
                      {src.published_at && (
                        <span className="text-zinc-500 text-[10px] font-mono">
                          {new Date(src.published_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-bold text-zinc-100 text-base hover:text-violet-400 hover:underline line-clamp-1 block"
                    >
                      {src.title}
                    </a>
                    <p className="text-zinc-400 text-xs leading-relaxed mt-2 line-clamp-2">
                      {src.content}
                    </p>
                  </div>

                  {/* Linking / Import Actions */}
                  <div className="w-full md:w-auto shrink-0 flex flex-row md:flex-col sm:items-center md:items-end gap-3 mt-4 md:mt-0 pt-4 md:pt-0 border-t md:border-t-0 border-zinc-900">
                    <div className="flex-1 sm:flex-initial">
                      <select
                        disabled={casesLoading || cases.length === 0}
                        value={selectedCaseIds[idx] || ""}
                        onChange={(e) => setSelectedCaseIds((prev) => ({ ...prev, [idx]: e.target.value }))}
                        className="w-full sm:w-48 px-3 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-300 text-xs focus:outline-none focus:border-violet-500"
                      >
                        <option value="">-- Link to Case --</option>
                        {cases.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.title}
                          </option>
                        ))}
                      </select>
                    </div>

                    <button
                      onClick={() => handleImport(idx, src)}
                      disabled={!selectedCaseIds[idx] || importingStates[idx]}
                      className="px-4 py-2 bg-violet-950/40 border border-violet-500/20 text-violet-400 hover:bg-violet-950 hover:text-violet-300 disabled:opacity-30 disabled:hover:bg-violet-950/40 disabled:hover:text-violet-400 rounded-lg text-xs font-bold transition-all duration-200 flex items-center justify-center gap-1.5"
                    >
                      {importingStates[idx] ? (
                        <>
                          <svg className="animate-spin h-3 w-3 text-violet-400" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          Linking...
                        </>
                      ) : (
                        "Import Source"
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
