import { AxiosHeaders } from "axios";
import { client } from "./api";

export interface ExpensePrediction {
  predicted_expenses: number;
  income: number;
  savings_potential: number;
  insights_available: boolean;
  insights?: Array<{
    category: string;
    avg_percentage: number;
    suggestion?: string;
  }>;
}

export interface PredictionParams {
  income: number;
}

export interface InsightResponse {
  success: boolean;
  insights: Array<{
    id: number;
    user_id: number;
    income_range: string;
    category: string;
    avg_percentage: number;
    created_at: string;
    updated_at: string;
  }>;
}

export const trainModel = (auth: AxiosHeaders | undefined) => {
  return client.post('/train', {}, { headers: auth });
}

export const predictExpenses = (auth: AxiosHeaders | undefined, params: PredictionParams) => {
  return client.post('/expenses', params, { headers: auth });
}

export const getInsights = (auth: AxiosHeaders | undefined) => {
  return client.get('/insights', { headers: auth });
} 