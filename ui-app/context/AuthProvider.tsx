"use client";

import { createContext } from "react";

export const AuthContext = createContext({});

export function AuthProvider({
  children,
  signature,
}: {
  children: React.ReactNode;
  signature: string | null;
}) {
  return (
    <AuthContext.Provider value={{ "X-CSRF-TOKEN": signature }}>
      {children}
    </AuthContext.Provider>
  );
}