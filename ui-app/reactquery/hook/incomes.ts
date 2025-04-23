import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as IncomeServices from "@/services/incomes";
import { IncomeQueryKeys, IncomeFilters } from "../querykeys/incomes";
import { useAuth } from "@/hooks/useAuth";

export const useIncomes = (filters?: IncomeFilters) => {
  const auth = useAuth();
  return useQuery({
    queryKey: IncomeQueryKeys.list(filters),
    queryFn: () => IncomeServices.getIncomes(auth, filters),
    enabled: !!auth,
  });
};

export const useIncomeDetail = (id: number) => {
  const auth = useAuth();
  return useQuery({
    queryKey: IncomeQueryKeys.detail(id),
    queryFn: () => IncomeServices.getIncomeById(id, auth),
    enabled: !!auth && !!id,
  });
};

export const useCreateIncome = () => {
  const queryClient = useQueryClient();
  const auth = useAuth();

  return useMutation({
    mutationFn: (params: IncomeServices.IncomeCreateParams) =>
      IncomeServices.createIncome(params, auth),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: IncomeQueryKeys.lists() });
    },
    onError: console.log,
  });
};
