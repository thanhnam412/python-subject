import { useMutation, useQuery } from "@tanstack/react-query";
import * as PredictionServices from "@/services/predictions";
import { PredictionQueryKeys, PredictionParams } from "../querykeys/predictions";
import { useAuth } from "@/hooks/useAuth";

export const useTrainModel = () => {
  const auth = useAuth();
  
  return useMutation({
    mutationKey: PredictionQueryKeys.train(),
    mutationFn: () => PredictionServices.trainModel(auth),
    onError: console.log,
  });
};

export const usePredictExpenses = () => {
  const auth = useAuth();
  
  return useMutation({
    mutationKey: PredictionQueryKeys.predict(),
    mutationFn: (params: PredictionParams) => 
      PredictionServices.predictExpenses(auth, params),
    onError: console.log,
  });
};

export const useInsights = () => {
  const auth = useAuth();
  return useQuery({
    queryKey: PredictionQueryKeys.insights(),
    queryFn: () => PredictionServices.getInsights(auth),
    enabled: !!auth,
  });
}; 