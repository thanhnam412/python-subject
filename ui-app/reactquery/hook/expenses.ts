import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as ExpenseServices from "@/services/expenses";
import { ExpenseQueryKeys, ExpenseFilters } from "../querykeys/expenses";
import { useAuth } from "@/hooks/useAuth";

export const useExpenses = (filters?: ExpenseFilters) => {
  const auth = useAuth();
  return useQuery({
    queryKey: ExpenseQueryKeys.list(filters),
    queryFn: () => ExpenseServices.getExpenses(auth, filters),
    enabled: !!auth,
  });
};

export const useExpenseDetail = (id: number) => {
  const auth = useAuth();
  return useQuery({
    queryKey: ExpenseQueryKeys.detail(id),
    queryFn: () => ExpenseServices.getExpenseById(id, auth),
    enabled: !!auth && !!id,
  });
};

export const useCreateExpense = () => {
  const queryClient = useQueryClient();
  const auth = useAuth();

  return useMutation({
    mutationFn: (params: ExpenseServices.ExpenseCreateParams) =>
      ExpenseServices.createExpense(params, auth),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ExpenseQueryKeys.lists() });
    },
    onError: console.log,
  });
};
