import { AxiosHeaders } from "axios";
import { client } from "./api";

export interface Expense {
  id: number;
  amount: number;
  description: string;
  category: string;
  date: string;
}

export interface ExpenseCreateParams {
  amount: number;
  description: string;
  category_id: number;
  date: string;
}

export interface ExpenseCategory {
  id: number;
  name: string;
  description?: string;
}

export interface ExpenseStatistics {
  total_expenses: number;
  by_category: Array<{
    category: string;
    total: number;
  }>;
  monthly_expenses: Array<{
    date: string;
    total: number;
  }>;
}

export const getExpenses = (auth: AxiosHeaders | undefined) => {
  return client.get('/expenses', { headers: auth });
}

export const getExpenseById = (id: number, auth: AxiosHeaders | undefined) => {
  return client.get(`/expenses/${id}`, { headers: auth });
}

export const createExpense = (params: ExpenseCreateParams, auth: AxiosHeaders | undefined) => {
  return client.post('/expenses', params, { headers: auth });
}

export const getExpenseStatistics = (auth: AxiosHeaders | undefined) => {
  return client.get('/expenses/statistics', { headers: auth });
}

export const getExpenseCategories = (auth: AxiosHeaders | undefined) => {
  return client.get('/expenses/categories', { headers: auth });
} 