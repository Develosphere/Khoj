import { supabase } from "../lib/supabase";

declare var process: { env: Record<string, string | undefined> };

const BACKEND_API_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8000";

async function request(endpoint: string, options: RequestInit = {}) {
  // 1. Get active session to extract access token
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;

  // 2. Build headers
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const url = `${BACKEND_API_URL}${endpoint}`;

  // 3. Perform fetch
  const response = await fetch(url, {
    ...options,
    headers,
  });

  // 4. Handle response errors
  if (!response.ok) {
    let errorDetail = "API request failed";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch {
      errorDetail = response.statusText;
    }
    throw new Error(errorDetail);
  }

  // 5. Parse JSON response if not empty
  if (response.status === 204 || response.headers.get("content-length") === "0") {
    return null;
  }
  return response.json();
}

export interface CasePayload {
  title: string;
  description?: string;
}

export interface CaseUpdatePayload {
  title?: string;
  description?: string;
  status?: "active" | "archived";
}

export interface DashboardStats {
  total_cases: number;
  active_cases: number;
  total_sources: number;
  total_evidence: number;
  total_theories: number;
}

export const apiService = {
  /**
   * Fetch all cases/investigations.
   */
  async getCases() {
    return request("/api/v1/cases/");
  },

  /**
   * Fetch detailed case by ID.
   */
  async getCaseDetails(caseId: string) {
    return request(`/api/v1/cases/${caseId}`);
  },

  /**
   * Create a new case.
   */
  async createCase(payload: CasePayload) {
    return request("/api/v1/cases/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Update metadata fields of a case.
   */
  async updateCase(caseId: string, payload: CaseUpdatePayload) {
    return request(`/api/v1/cases/${caseId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Delete a case.
   */
  async deleteCase(caseId: string) {
    return request(`/api/v1/cases/${caseId}`, {
      method: "DELETE",
    });
  },

  /**
   * Fetch dashboard metrics statistics.
   */
  async getDashboardStats() {
    return request("/api/v1/dashboard/stats");
  },

  /**
   * Run the complete AI investigation analysis pipeline.
   */
  async analyzeCase(caseId: string) {
    return request(`/api/v1/cases/${caseId}/analyze`, {
      method: "POST",
    });
  },

  /**
   * Search real-time news articles from the backend scrapers.
   */
  async searchSources(query: string) {
    return request(`/api/v1/investigations/sources?case_name=${encodeURIComponent(query)}`);
  },

  /**
   * Manually import/link a source to a specific case.
   */
  async addSourceToCase(caseId: string, source: any) {
    return request(`/api/v1/cases/${caseId}/sources`, {
      method: "POST",
      body: JSON.stringify(source),
    });
  },
};
