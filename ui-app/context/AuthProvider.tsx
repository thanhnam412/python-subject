"use client";

import { AxiosHeaders } from "axios";
import { createContext, useContext } from "react";

const AuthContext = createContext({});

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

export const useAuth = () => {
  const auth = useContext(AuthContext);
  return auth as unknown as AxiosHeaders;
};
