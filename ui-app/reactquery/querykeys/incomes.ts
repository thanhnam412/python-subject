export interface IncomeFilters {
  startDate?: string;
  endDate?: string;
  source?: string;
}

export const IncomeQueryKeys = {
  all: ["incomes"],
  lists: () => [...IncomeQueryKeys.all, "list"],
  list: (filters?: IncomeFilters) => [...IncomeQueryKeys.lists(), { ...filters }],
  details: () => [...IncomeQueryKeys.all, "detail"],
  detail: (id: number) => [...IncomeQueryKeys.details(), id],
  statistics: () => [...IncomeQueryKeys.all, "statistics"],
}; 