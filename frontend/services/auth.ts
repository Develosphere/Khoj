import { supabase } from '../lib/supabase'

type Credentials = { email: string; password: string }
type SignUpInput = Credentials & { fullName: string }

export const authService = {
  async signIn({ email, password }: Credentials) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    return data
  },

  async signUp({ email, password, fullName }: SignUpInput) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: fullName } },
    })
    if (error) throw error
    return data
  },

  async signInWithGoogle() {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/dashboard` },
    })
    if (error) throw error
    return data
  },

  async signOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  },

  async getSession() {
    const { data, error } = await supabase.auth.getSession()
    if (error) throw error
    return data.session
  },

  async getAssuranceLevel() {
    const { data, error } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel()
    if (error) throw error
    return data
  },

  async listFactors() {
    const { data, error } = await supabase.auth.mfa.listFactors()
    if (error) throw error
    return data
  },

  async enrollTOTP(friendlyName: string) {
    const { data, error } = await supabase.auth.mfa.enroll({
      factorType: 'totp',
      friendlyName,
    })
    if (error) throw error
    return data
  },

  async challengeAndVerifyTOTP(factorId: string, code: string) {
    const challenge = await supabase.auth.mfa.challenge({ factorId })
    if (challenge.error) throw challenge.error
    const { data, error } = await supabase.auth.mfa.verify({
      factorId,
      challengeId: challenge.data.id,
      code,
    })
    if (error) throw error
    return data
  },

  async unenrollFactor(factorId: string) {
    const { data, error } = await supabase.auth.mfa.unenroll({ factorId })
    if (error) throw error
    return data
  },
}
