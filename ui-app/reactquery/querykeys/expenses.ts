export interface ExpenseFilters {
  startDate?: string;
  endDate?: string;
  category?: string;
}

export const ExpenseQueryKeys = {
  all: ["expenses"],
  lists: () => [...ExpenseQueryKeys.all, "list"],
  list: (filters?: ExpenseFilters) => [...ExpenseQueryKeys.lists(), { ...filters }],
  details: () => [...ExpenseQueryKeys.all, "detail"],
  detail: (id: number) => [...ExpenseQueryKeys.details(), id],
  statistics: () => [...ExpenseQueryKeys.all, "statistics"],
  categories: () => [...ExpenseQueryKeys.all, "categories"],
}; 