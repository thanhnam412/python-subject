import { AxiosHeaders } from "axios";
import { client } from "./api";

export interface FinancialSummary {
  total_income: number;
  total_expense: number;
  total_debt: number;
  balance: number;
  date: string;
}

export interface DailySummary {
  date: string;
  total_income: number;
  total_expense: number;
  total_debt: number;
  balance: number;
}

export interface SummaryResponse {
  items: FinancialSummary[];
  total: number;
  pages: number;
  current_page: number;
}

export interface StatisticsResponse {
  daily_summaries: DailySummary[];
}

export const getSummaries = (auth: AxiosHeaders | undefined, period: string = 'month', page: number = 1, perPage: number = 10) => {
  const queryParams = new URLSearchParams();
  queryParams.append('period', period);
  queryParams.append('page', page.toString());
  queryParams.append('per_page', perPage.toString());
  
  return client.get(`/summaries?${queryParams.toString()}`, { headers: auth });
}

export const getCurrentSummary = (auth: AxiosHeaders | undefined) => {
  return client.get('/summaries/current', { headers: auth });
}

export const getSummaryStatistics = (auth: AxiosHeaders | undefined, period: string = 'month') => {
  return client.get(`/summaries/statistics?period=${period}`, { headers: auth });
} 