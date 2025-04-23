import { AxiosHeaders } from "axios";
import { client } from "./api";

export interface Income {
  id: number;
  amount: number;
  description: string | null
  source: string;
  date: Date;
  user_id: null
  created_at: Date
  updated_at: Date
}

export interface IncomeCreateParams {
  amount: number;
  source: string;
  description?: string;
  date?: Date;
}

export const getIncomes = (auth: AxiosHeaders | undefined, params?: Record<string, string>) => {
  const query = new URLSearchParams(params).toString()
  return client.get(`/incomes?${query}`, { headers: auth });
}

export const getIncomeById = (id: number, auth: AxiosHeaders | undefined) => {
  return client.get(`/incomes/${id}`, { headers: auth });
}

export const createIncome = (params: IncomeCreateParams, auth: AxiosHeaders | undefined) => {
  return client.post('/incomes', params, { headers: auth });
}
