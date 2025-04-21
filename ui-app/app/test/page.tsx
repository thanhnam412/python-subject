"use client";

import { Button } from "@/components/ui/button";
import { useState } from "react";
import {
  useCreateDebt,
  useDebts,
  useDebtDetail,
  useUpdateDebt,
  useDebtStatistics,
} from "@/reactquery/hook/debts";
import {
  useCreateExpense,
  useExpenses,
  useExpenseDetail,
  useExpenseStatistics,
} from "@/reactquery/hook/expenses";
import {
  useCreateIncome,
  useIncomes,
  useIncomeDetail,
  useIncomeStatistics,
} from "@/reactquery/hook/incomes";
import {
  MOCK_DEBT,
  MOCK_DEBT_UPDATE,
  MOCK_EXPENSE,
  MOCK_INCOME,
  MOCK_PREDICT_EXPENSES_REQUEST,
} from "@/services/mock-data";

// Uncomment the summary and prediction hooks
import {
  useSummaries,
  useCurrentSummary,
  useSummaryStatistics,
} from "@/reactquery/hook/summary";

import {
  useTrainModel,
  usePredictExpenses,
  useInsights,
} from "@/reactquery/hook/predictions";

export default function TestPage() {
  const [debtId, setDebtId] = useState<number>(1);
  const [expenseId, setExpenseId] = useState<number>(1);
  const [incomeId, setIncomeId] = useState<number>(1);
  const [income, setIncome] = useState<number>(
    MOCK_PREDICT_EXPENSES_REQUEST.income
  );

  // Debt Hooks
  const { mutateAsync: createDebt } = useCreateDebt();
  const { mutateAsync: updateDebt } = useUpdateDebt();
  const { data: debtsData, refetch: refetchDebts } = useDebts();
  const { data: debtDetail, invalidateQueries: refetchDebtDetail } =
    useDebtDetail(debtId);
  const { data: debtStats, refetch: refetchDebtStats } = useDebtStatistics();

  // Expense Hooks
  const { mutateAsync: createExpense } = useCreateExpense();
  const { data: expensesData, refetch: refetchExpenses } = useExpenses();
  const { data: expenseDetail, refetch: refetchExpenseDetail } =
    useExpenseDetail(expenseId);
  const { data: expenseStats, refetch: refetchExpenseStats } =
    useExpenseStatistics();

  // Income Hooks
  const { mutateAsync: createIncome } = useCreateIncome();
  const { data: incomesData, refetch: refetchIncomes } = useIncomes();
  const { data: incomeDetail, refetch: refetchIncomeDetail } =
    useIncomeDetail(incomeId);
  const { data: incomeStats, refetch: refetchIncomeStats } =
    useIncomeStatistics();

  // Summary Hooks
  const { data: summaries, refetch: refetchSummaries } = useSummaries();
  const { data: currentSummary, refetch: refetchCurrentSummary } =
    useCurrentSummary();
  const { data: summaryStats, refetch: refetchSummaryStats } =
    useSummaryStatistics();

  // Prediction Hooks
  const { mutateAsync: trainModel } = useTrainModel();
  const { mutateAsync: predictExpenses } = usePredictExpenses();
  const { data: insightsData, refetch: refetchInsights } = useInsights();

  // Debt Handlers
  const handleCreateDebt = async () => {
    try {
      const result = await createDebt(MOCK_DEBT);
      console.log("Debt created:", result);
    } catch (error) {
      console.error("Error creating debt:", error);
    }
  };

  const handleGetDebts = async () => {
    try {
      const result = await refetchDebts();
      console.log("All debts:", result.data);
    } catch (error) {
      console.error("Error fetching debts:", error);
    }
  };

  const handleGetDebtDetail = async () => {
    try {
      await refetchDebtDetail();
    } catch (error) {
      console.error("Error fetching debt detail:", error);
    }
  };

  const handleUpdateDebt = async () => {
    try {
      const debtUpdate = { ...MOCK_DEBT_UPDATE, id: debtId };
      const result = await updateDebt(debtUpdate);
      console.log("Debt updated:", result);
    } catch (error) {
      console.error("Error updating debt:", error);
    }
  };

  const handleGetDebtStats = async () => {
    try {
      const result = await refetchDebtStats();
      console.log("Debt statistics:", result.data);
    } catch (error) {
      console.error("Error fetching debt stats:", error);
    }
  };

  // Expense Handlers
  const handleCreateExpense = async () => {
    try {
      // Convert the mock data to the correct format
      const expenseParams = {
        amount: MOCK_EXPENSE.amount,
        description: MOCK_EXPENSE.description,
        category_id: 1, // Assuming 1 is a valid category ID
        date: MOCK_EXPENSE.date,
      };
      const result = await createExpense(expenseParams);
      console.log("Expense created:", result);
    } catch (error) {
      console.error("Error creating expense:", error);
    }
  };

  const handleGetExpenses = async () => {
    try {
      const result = await refetchExpenses();
      console.log("All expenses:", result.data);
    } catch (error) {
      console.error("Error fetching expenses:", error);
    }
  };

  const handleGetExpenseDetail = async () => {
    try {
      const result = await refetchExpenseDetail();
      console.log("Expense detail:", result.data);
    } catch (error) {
      console.error("Error fetching expense detail:", error);
    }
  };

  const handleGetExpenseStats = async () => {
    try {
      const result = await refetchExpenseStats();
      console.log("Expense statistics:", result.data);
    } catch (error) {
      console.error("Error fetching expense stats:", error);
    }
  };

  // Income Handlers
  const handleCreateIncome = async () => {
    try {
      const result = await createIncome(MOCK_INCOME);
      console.log("Income created:", result);
    } catch (error) {
      console.error("Error creating income:", error);
    }
  };

  const handleGetIncomes = async () => {
    try {
      const result = await refetchIncomes();
      console.log("All incomes:", result.data);
    } catch (error) {
      console.error("Error fetching incomes:", error);
    }
  };

  const handleGetIncomeDetail = async () => {
    try {
      const result = await refetchIncomeDetail();
      console.log("Income detail:", result.data);
    } catch (error) {
      console.error("Error fetching income detail:", error);
    }
  };

  const handleGetIncomeStats = async () => {
    try {
      const result = await refetchIncomeStats();
      console.log("Income statistics:", result.data);
    } catch (error) {
      console.error("Error fetching income stats:", error);
    }
  };

  // Summary Handlers
  const handleGetSummaries = async () => {
    try {
      const result = await refetchSummaries();
      console.log("Summaries:", result.data);
    } catch (error) {
      console.error("Error fetching summaries:", error);
    }
  };

  const handleGetCurrentSummary = async () => {
    try {
      const result = await refetchCurrentSummary();
      console.log("Current summary:", result.data);
    } catch (error) {
      console.error("Error fetching current summary:", error);
    }
  };

  const handleGetSummaryStats = async () => {
    try {
      const result = await refetchSummaryStats();
      console.log("Summary statistics:", result.data);
    } catch (error) {
      console.error("Error fetching summary stats:", error);
    }
  };

  // Prediction Handlers
  const handleTrainModel = async () => {
    try {
      // Adding empty object as parameter to satisfy linter
      const result = await trainModel({});
      console.log("Model trained:", result);
    } catch (error) {
      console.error("Error training model:", error);
    }
  };

  const handlePredictExpenses = async () => {
    try {
      const result = await predictExpenses({ income });
      console.log("Expense prediction:", result);
    } catch (error) {
      console.error("Error predicting expenses:", error);
    }
  };

  const handleGetInsights = async () => {
    try {
      const result = await refetchInsights();
      console.log("Prediction insights:", result.data);
    } catch (error) {
      console.error("Error fetching insights:", error);
    }
  };

  return (
    <div className="space-y-8 p-4">
      {/* IDs Input Section */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-2 border rounded">
          <label className="block mb-2">Debt ID:</label>
          <input
            type="number"
            value={debtId}
            onChange={(e) => setDebtId(Number(e.target.value))}
            className="border p-2 rounded w-full"
          />
        </div>

        <div className="p-2 border rounded">
          <label className="block mb-2">Expense ID:</label>
          <input
            type="number"
            value={expenseId}
            onChange={(e) => setExpenseId(Number(e.target.value))}
            className="border p-2 rounded w-full"
          />
        </div>

        <div className="p-2 border rounded">
          <label className="block mb-2">Income ID:</label>
          <input
            type="number"
            value={incomeId}
            onChange={(e) => setIncomeId(Number(e.target.value))}
            className="border p-2 rounded w-full"
          />
        </div>

        <div className="p-2 border rounded">
          <label className="block mb-2">Income for Prediction:</label>
          <input
            type="number"
            value={income}
            onChange={(e) => setIncome(Number(e.target.value))}
            className="border p-2 rounded w-full"
          />
        </div>
      </div>

      {/* Mock Data Display */}
      <div className="border rounded-md p-4">
        <h2 className="text-xl font-bold mb-2">Mock Data</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border p-3 rounded-md">
            <h3 className="font-semibold mb-2">Debt Mock</h3>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto max-h-40">
              {JSON.stringify(MOCK_DEBT, null, 2)}
            </pre>
          </div>
          <div className="border p-3 rounded-md">
            <h3 className="font-semibold mb-2">Expense Mock</h3>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto max-h-40">
              {JSON.stringify(MOCK_EXPENSE, null, 2)}
            </pre>
          </div>
          <div className="border p-3 rounded-md">
            <h3 className="font-semibold mb-2">Income Mock</h3>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto max-h-40">
              {JSON.stringify(MOCK_INCOME, null, 2)}
            </pre>
          </div>
        </div>
      </div>

      {/* Debt APIs */}
      <div className="border rounded-md p-4">
        <h2 className="text-xl font-bold mb-2">Debt APIs</h2>
        <div className="flex flex-wrap gap-2">
          <Button onClick={handleCreateDebt}>useCreateDebt</Button>
          <Button onClick={handleGetDebts}>useDebts</Button>
          <Button onClick={handleGetDebtDetail}>useDebtDetail</Button>
          <Button onClick={handleUpdateDebt}>useUpdateDebt</Button>
          <Button onClick={handleGetDebtStats}>useDebtStatistics</Button>
        </div>
      </div>

      {/* Expense APIs */}
      <div className="border rounded-md p-4">
        <h2 className="text-xl font-bold mb-2">Expense APIs</h2>
        <div className="flex flex-wrap gap-2">
          <Button onClick={handleCreateExpense}>useCreateExpense</Button>
          <Button onClick={handleGetExpenses}>useExpenses</Button>
          <Button onClick={handleGetExpenseDetail}>useExpenseDetail</Button>
          <Button onClick={handleGetExpenseStats}>useExpenseStatistics</Button>
        </div>
      </div>

      {/* Income APIs */}
      <div className="border rounded-md p-4">
        <h2 className="text-xl font-bold mb-2">Income APIs</h2>
        <div className="flex flex-wrap gap-2">
          <Button onClick={handleCreateIncome}>useCreateIncome</Button>
          <Button onClick={handleGetIncomes}>useIncomes</Button>
          <Button onClick={handleGetIncomeDetail}>useIncomeDetail</Button>
          <Button onClick={handleGetIncomeStats}>useIncomeStatistics</Button>
        </div>
      </div>

      {/* Summary APIs */}
      <div className="border rounded-md p-4">
        <h2 className="text-xl font-bold mb-2">Summary APIs</h2>
        <div className="flex flex-wrap gap-2">
          <Button onClick={handleGetSummaries}>useSummaries</Button>
          <Button onClick={handleGetCurrentSummary}>useCurrentSummary</Button>
          <Button onClick={handleGetSummaryStats}>useSummaryStatistics</Button>
        </div>
      </div>

      {/* Prediction APIs */}
      <div className="border rounded-md p-4">
        <h2 className="text-xl font-bold mb-2">Prediction APIs</h2>
        <div className="flex flex-wrap gap-2">
          <Button onClick={handleTrainModel}>useTrainModel</Button>
          <Button onClick={handlePredictExpenses}>usePredictExpenses</Button>
          <Button onClick={handleGetInsights}>useInsights</Button>
        </div>
      </div>

      {/* Results Display */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {debtDetail && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Debt Detail</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(debtDetail, null, 2)}
            </pre>
          </div>
        )}

        {debtsData && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">All Debts</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(debtsData, null, 2)}
            </pre>
          </div>
        )}

        {debtStats && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Debt Statistics</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(debtStats, null, 2)}
            </pre>
          </div>
        )}

        {expenseDetail && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Expense Detail</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(expenseDetail, null, 2)}
            </pre>
          </div>
        )}

        {expensesData && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">All Expenses</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(expensesData, null, 2)}
            </pre>
          </div>
        )}

        {expenseStats && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Expense Statistics</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(expenseStats, null, 2)}
            </pre>
          </div>
        )}

        {incomeDetail && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Income Detail</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(incomeDetail, null, 2)}
            </pre>
          </div>
        )}

        {incomesData && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">All Incomes</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(incomesData, null, 2)}
            </pre>
          </div>
        )}

        {incomeStats && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Income Statistics</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(incomeStats, null, 2)}
            </pre>
          </div>
        )}

        {summaries && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Summaries</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(summaries, null, 2)}
            </pre>
          </div>
        )}

        {currentSummary && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Current Summary</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(currentSummary, null, 2)}
            </pre>
          </div>
        )}

        {summaryStats && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Summary Statistics</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(summaryStats, null, 2)}
            </pre>
          </div>
        )}

        {insightsData && (
          <div className="p-4 border rounded">
            <h2 className="text-lg font-bold mb-2">Prediction Insights</h2>
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-60">
              {JSON.stringify(insightsData, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
