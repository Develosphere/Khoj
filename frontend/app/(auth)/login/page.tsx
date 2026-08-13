import LoginForm from "../../../components/auth/login-form";

export const metadata = {
  title: "Login - KHOJ AI Platform",
  description: "Sign in to KHOJ AI Investigation & 3D Reconstruction Platform.",
};

export default function LoginPage() {
  return (
    <main className="relative flex items-center justify-center min-h-screen bg-black overflow-hidden font-sans">
      {/* Visual background glows */}
      <div className="absolute w-[500px] h-[500px] rounded-full bg-violet-600/10 blur-[120px] top-[-100px] left-[-100px] pointer-events-none"></div>
      <div className="absolute w-[500px] h-[500px] rounded-full bg-indigo-600/10 blur-[120px] bottom-[-100px] right-[-100px] pointer-events-none"></div>
      
      {/* Decorative tech grid pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.08),rgba(255,255,255,0))] pointer-events-none"></div>

      <div className="relative z-10 w-full flex justify-center px-4 py-12">
        <LoginForm />
      </div>
    </main>
  );
}
