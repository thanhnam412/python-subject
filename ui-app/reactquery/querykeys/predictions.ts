export interface PredictionParams {
  income: number;
}

export const PredictionQueryKeys = {
  all: ["predictions"],
  train: () => [...PredictionQueryKeys.all, "train"],
  predict: (params?: PredictionParams) => 
    [...PredictionQueryKeys.all, "predict", { ...params }],
  insights: () => [...PredictionQueryKeys.all, "insights"],
}; 