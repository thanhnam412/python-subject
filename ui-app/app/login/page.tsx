import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <div className="bg-stone-100 flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10 dark:bg-stone-800">
      <LoginForm />
    </div>
  );
}
