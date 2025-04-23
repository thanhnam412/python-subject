import { AxiosHeaders } from "axios";
import { client } from "./api";

export interface Expense {
  id: number;
  amount: number;
  description: string;
  date: string;
}

export interface ExpenseCreateParams {
  amount: number;
  title: string;
  description?: string;
  date?: Date;
}

export const getExpenses = (auth: AxiosHeaders | undefined, params?: Record<string, string>) => {
  const query = new URLSearchParams(params).toString()
  return client.get(`/expenses?${query}`, { headers: auth });
}

export const getExpenseById = (id: number, auth: AxiosHeaders | undefined) => {
  return client.get(`/expenses/${id}`, { headers: auth });
}

export const createExpense = (params: ExpenseCreateParams, auth: AxiosHeaders | undefined) => {
  return client.post('/expenses', params, { headers: auth });
}
