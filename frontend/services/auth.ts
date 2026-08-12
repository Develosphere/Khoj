import { supabase } from "../lib/supabase";

export interface SignUpParams {
  email: string;
  password: string;
  fullName: string;
}

export interface SignInParams {
  email: string;
  password: string;
}

export const authService = {
  /**
   * Sign up a new user with email, password, and full name metadata.
   */
  async signUp({ email, password, fullName }: SignUpParams) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
      },
    });
    if (error) throw error;
    return data;
  },

  /**
   * Sign in an existing user with email and password.
   */
  async signIn({ email, password }: SignInParams) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
    return data;
  },

  /**
   * Trigger Google OAuth sign-in.
   */
  async signInWithGoogle() {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: typeof window !== "undefined" ? `${window.location.origin}/dashboard` : undefined,
      },
    });
    if (error) throw error;
    return data;
  },

  /**
   * Sign out the currently authenticated user.
   */
  async signOut() {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  },

  /**
   * Get the current user profile.
   */
  async getUser() {
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error) throw error;
    return user;
  },

  /**
   * Get the current session.
   */
  async getSession() {
    const { data: { session }, error } = await supabase.auth.getSession();
    if (error) throw error;
    return session;
  },

  /**
   * Get current authenticator assurance level (AAL) for 2FA.
   * returns: { currentLevel: 'aal1' | 'aal2', nextLevel: 'aal1' | 'aal2' }
   */
  async getAssuranceLevel() {
    const { data, error } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel();
    if (error) throw error;
    return data;
  },

  /**
   * List enrolled MFA factors for the current user.
   */
  async listFactors() {
    const { data, error } = await supabase.auth.mfa.listFactors();
    if (error) throw error;
    return data;
  },

  /**
   * Enroll a new TOTP factor.
   * Returns: { id: factorId, type: 'totp', totp: { qr_code: string (SVG), secret: string } }
   */
  async enrollTOTP(factorName: string = "TOTP Factor") {
    const { data, error } = await supabase.auth.mfa.enroll({
      factorType: "totp",
      friendlyName: factorName,
    });
    if (error) throw error;
    return data;
  },

  /**
   * Challenge and verify a TOTP code during enrollment or login to activate/verify MFA.
   */
  async challengeAndVerifyTOTP(factorId: string, code: string) {
    // 1. Create a challenge for the factor
    const { data: challengeData, error: challengeError } = await supabase.auth.mfa.challenge({
      factorId,
    });
    if (challengeError) throw challengeError;

    // 2. Verify the challenge code
    const { data: verifyData, error: verifyError } = await supabase.auth.mfa.verify({
      factorId,
      challengeId: challengeData.id,
      code,
    });
    if (verifyError) throw verifyError;

    return verifyData;
  },

  /**
   * Unenroll/remove an MFA factor.
   */
  async unenrollFactor(factorId: string) {
    const { data, error } = await supabase.auth.mfa.unenroll({
      factorId,
    });
    if (error) throw error;
    return data;
  },
};
