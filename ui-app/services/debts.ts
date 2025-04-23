import { AxiosHeaders } from "axios";
import { client } from "./api"

export interface Debt {
  id: number;
  amount: number;
  description: string;
  interest_rate: number;
  due_date: string;
  monthly_payment: number;
}

export interface DebtCreateParams {
  amount: number;
  title: string;
  description?: string;
  interest_rate: number;
}


export const getDebts = (auth: AxiosHeaders | undefined, params?: Record<string, string>) => {
  const query = new URLSearchParams(params).toString()
  return client.get(`/debts?${query}`, { headers: auth });
}

export const getDebtById = (id: number, auth: AxiosHeaders | undefined) => {
  return client.get(`/debts/${id}`, { headers: auth });
}

export const createDebt = (params: DebtCreateParams, auth: AxiosHeaders | undefined) => {
  return client.post('/debts', params, { headers: auth });
}
