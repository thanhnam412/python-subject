import { useQuery } from "@tanstack/react-query"
import * as TokenServices from "@/services/debts";

import { DebtsQueryKeys } from "../querykeys/debts";
import { useAuth } from "@/hooks/useAuth";


export const useCreateDebts = () => {
  const auth = useAuth()

  return useQuery({
    queryKey: DebtsQueryKeys.create,
    queryFn: () => TokenServices.postCreateDebts(auth),
    enabled: !!auth
  })
}