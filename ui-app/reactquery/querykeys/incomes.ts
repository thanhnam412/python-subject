export type IncomeFilters = Record<string, string>

export const IncomeQueryKeys = {
  all: ["incomes"],
  lists: () => [...IncomeQueryKeys.all, "list"],
  list: (filters?: IncomeFilters) => [...IncomeQueryKeys.lists(), { ...filters }],
  details: () => [...IncomeQueryKeys.all, "detail"],
  detail: (id: number) => [...IncomeQueryKeys.details(), id],
}; 