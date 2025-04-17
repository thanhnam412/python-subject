"use client";

import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { AuthProvider } from "@/context/AuthProvider";
import { ReactNode } from "react";

interface ProviderProps {
  children: ReactNode;
  signature: string | null;
}

const queryClient = new QueryClient();

const Providers = ({ children, signature }: ProviderProps) => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider signature={signature}>{children}</AuthProvider>
    </QueryClientProvider>
  );
};

export default Providers;
