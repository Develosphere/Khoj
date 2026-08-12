import { useEffect, useState, useCallback } from "react";
import { User, Session } from "@supabase/supabase-js";
import { authService } from "../services/auth";
import { supabase } from "../lib/supabase";

export interface AuthState {
  user: User | null;
  session: Session | null;
  loading: boolean;
  mfaLevel: "aal1" | "aal2" | null;
  mfaRequired: boolean;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    session: null,
    loading: true,
    mfaLevel: null,
    mfaRequired: false,
  });

  const checkMfaStatus = useCallback(async () => {
    try {
      const assurance = await authService.getAssuranceLevel();
      const factors = await authService.listFactors();
      
      const mfaRequired = 
        assurance.nextLevel === "aal2" && 
        assurance.currentLevel !== "aal2" && 
        factors.totp.length > 0;

      return {
        mfaLevel: assurance.currentLevel as "aal1" | "aal2",
        mfaRequired,
      };
    } catch (err) {
      console.error("Error checking MFA status:", err);
      return { mfaLevel: null, mfaRequired: false };
    }
  }, []);

  const refreshState = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true }));
    try {
      const session = await authService.getSession();
      const user = session?.user || null;
      
      let mfaLevel: "aal1" | "aal2" | null = null;
      let mfaRequired = false;

      if (user) {
        const mfa = await checkMfaStatus();
        mfaLevel = mfa.mfaLevel;
        mfaRequired = mfa.mfaRequired;
      }

      setState({
        user,
        session,
        loading: false,
        mfaLevel,
        mfaRequired,
      });
    } catch (err) {
      console.error("Error refreshing auth state:", err);
      setState({
        user: null,
        session: null,
        loading: false,
        mfaLevel: null,
        mfaRequired: false,
      });
    }
  }, [checkMfaStatus]);

  useEffect(() => {
    // Check initial session
    refreshState();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      const user = session?.user || null;
      
      let mfaLevel: "aal1" | "aal2" | null = null;
      let mfaRequired = false;

      if (user) {
        const mfa = await checkMfaStatus();
        mfaLevel = mfa.mfaLevel;
        mfaRequired = mfa.mfaRequired;
      }

      setState({
        user,
        session,
        loading: false,
        mfaLevel,
        mfaRequired,
      });
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [refreshState, checkMfaStatus]);

  return {
    ...state,
    refreshState,
  };
}
