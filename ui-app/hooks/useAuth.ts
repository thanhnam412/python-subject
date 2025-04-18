import { AuthContext } from "@/context/AuthProvider";
import { AxiosHeaders } from "axios";
import { useContext } from "react";

export const useAuth = () => {
  const auth = useContext(AuthContext) as { 'X-CSRF-TOKEN': string | null };

  if (auth?.['X-CSRF-TOKEN']) return auth as unknown as AxiosHeaders;
  return undefined
};
