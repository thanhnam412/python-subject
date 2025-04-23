export type DebtFilters = Record<string, string>

export const DebtQueryKeys = {
  all: ["debts"],
  lists: () => [...DebtQueryKeys.all, "list"],
  list: (filters?: DebtFilters) => [...DebtQueryKeys.lists(), { ...filters }],
  details: () => [...DebtQueryKeys.all, "detail"],
  detail: (id: number) => [...DebtQueryKeys.details(), id],
};
