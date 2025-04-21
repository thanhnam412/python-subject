import { AxiosHeaders } from "axios";
import { client } from "./api";

export interface Income {
  id: number;
  amount: number;
  description: string;
  source: string;
  date: string;
}

export interface IncomeCreateParams {
  amount: number;
  description: string;
  source: string;
  date: string;
}

export interface IncomeStatistics {
  total_income: number;
  by_source: Array<{
    source: string;
    total: number;
  }>;
  monthly_income: Array<{
    date: string;
    total: number;
  }>;
}

export const getIncomes = (auth: AxiosHeaders | undefined) => {
  return client.get('/incomes', { headers: auth });
}

export const getIncomeById = (id: number, auth: AxiosHeaders | undefined) => {
  return client.get(`/incomes/${id}`, { headers: auth });
}

export const createIncome = (params: IncomeCreateParams, auth: AxiosHeaders | undefined) => {
  return client.post('/incomes', params, { headers: auth });
}

export const getIncomeStatistics = (auth: AxiosHeaders | undefined) => {
  return client.get('/incomes/statistics', { headers: auth });
} 