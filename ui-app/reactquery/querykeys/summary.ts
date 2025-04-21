export interface SummaryFilters {
  period?: string;
  page?: number;
  perPage?: number;
}

export const SummaryQueryKeys = {
  all: ["summary"],
  list: (filters?: SummaryFilters) => [...SummaryQueryKeys.all, "list", { ...filters }],
  current: () => [...SummaryQueryKeys.all, "current"],
  statistics: (period?: string) => [...SummaryQueryKeys.all, "statistics", { period }],
}; 