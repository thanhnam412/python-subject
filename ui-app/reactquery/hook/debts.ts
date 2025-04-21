import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import * as DebtServices from "@/services/debts";

import { DebtQueryKeys, DebtFilters } from "../querykeys/debts";
import { useAuth } from "@/hooks/useAuth";

export const useDebts = (filters?: DebtFilters) => {
  const auth = useAuth();
  return useQuery({
    queryKey: DebtQueryKeys.list(filters),
    queryFn: () => DebtServices.getDebts(auth,filters),
    enabled: !!auth,
  });
};

export const useDebtDetail = (id: number) => {
  const auth = useAuth();
  const queryClient = useQueryClient()
  const query = useQuery({
    queryKey: DebtQueryKeys.detail(id),
    queryFn: () => DebtServices.getDebtById(id, auth),
    enabled: !!auth && !!id,
  });

  const invalidateQueries = () => {
    return queryClient.invalidateQueries({ queryKey: DebtQueryKeys.detail(id) })
  }

  return { ...query, invalidateQueries }
};

export const useCreateDebt = () => {
  const queryClient = useQueryClient();
  const auth = useAuth();

  return useMutation({
    mutationFn: (params: DebtServices.DebtCreateParams) =>
      DebtServices.createDebt(params, auth),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DebtQueryKeys.lists() });
    },
    onError: console.log,
  });
};

export const useUpdateDebt = () => {
  const queryClient = useQueryClient();
  const auth = useAuth();

  return useMutation({
    mutationFn: (params: DebtServices.DebtUpdateParams) =>
      DebtServices.updateDebt(params, auth),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: DebtQueryKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: DebtQueryKeys.lists() });
    },
    onError: console.log,
  });
};

export const useDebtStatistics = () => {
  const auth = useAuth();
  return useQuery({
    queryKey: DebtQueryKeys.statistics(),
    queryFn: () => DebtServices.getDebtStatistics(auth),
    enabled: !!auth,
  });
};