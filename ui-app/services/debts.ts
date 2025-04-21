import { AxiosHeaders } from "axios";
import { client } from "./api"
import { DebtFilters } from "@/reactquery/querykeys/debts";

export interface Debt {
  id: number;
  amount: number;
  description: string;
  interest_rate: number;
  due_date: string;
  monthly_payment: number;
  category: string;
}

export interface DebtCreateParams {
  amount: number;
  description: string;
  interest_rate: number;
  due_date: string;
  monthly_payment: number;
  category: string;
}

export interface DebtUpdateParams {
  id: number;
  amount?: number;
  description?: string;
  interest_rate?: number;
  due_date?: string;
  monthly_payment?: number;
  category?: string;
  is_paid?: boolean;
}

export interface DebtStatistics {
  total_debt: number;
  upcoming_debts: Array<{
    date: string;
    total: number;
  }>;
}

export const getDebts = (auth: AxiosHeaders | undefined, params?: DebtFilters) => {
  const query = new URLSearchParams(params as any).toString()
  return client.get(`/debts?${query}`, { headers: auth });
}

export const getDebtById = (id: number, auth: AxiosHeaders | undefined) => {
  return client.get(`/debts/${id}`, { headers: auth });
}

export const createDebt = (params: DebtCreateParams, auth: AxiosHeaders | undefined) => {
  return client.post('/debts', params, { headers: auth });
}

export const updateDebt = ({ id, ...params }: DebtUpdateParams, auth: AxiosHeaders | undefined) => {
  return client.put(`/debts/${id}`, params, { headers: auth });
}

export const getDebtStatistics = (auth: AxiosHeaders | undefined) => {
  return client.get('/debts/statistics', { headers: auth });
}