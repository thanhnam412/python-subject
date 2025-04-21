import { useQuery } from "@tanstack/react-query";
import * as SummaryServices from "@/services/summary";
import { SummaryQueryKeys } from "../querykeys/summary";
import { useAuth } from "@/hooks/useAuth";

export const useSummaries = (period: string = 'month', page: number = 1, perPage: number = 10) => {
  const auth = useAuth();
  return useQuery({
    queryKey: SummaryQueryKeys.list({ period, page, perPage }),
    queryFn: () => SummaryServices.getSummaries(auth, period, page, perPage),
    enabled: !!auth,
  });
};

export const useCurrentSummary = () => {
  const auth = useAuth();
  return useQuery({
    queryKey: SummaryQueryKeys.current(),
    queryFn: () => SummaryServices.getCurrentSummary(auth),
    enabled: !!auth,
  });
};

export const useSummaryStatistics = (period: string = 'month') => {
  const auth = useAuth();
  return useQuery({
    queryKey: SummaryQueryKeys.statistics(period),
    queryFn: () => SummaryServices.getSummaryStatistics(auth, period),
    enabled: !!auth,
  });
}; 