/**
 * Mock data for testing API endpoints
 */

// Debt related mock data
export const MOCK_DEBT = {
  amount: 1000000,
  description: "Khoản vay mua nhà",
  interest_rate: 5.5,
  due_date: new Date().toISOString().split('T')[0],
  monthly_payment: 5000000,
  category: "Vay mua nhà"
};

export const MOCK_DEBT_UPDATE = {
  id: 1,
  amount: 1200000,
  description: "Khoản vay mua nhà (đã cập nhật)",
  is_paid: false
};

export const MOCK_DEBTS_RESPONSE = {
  items: [
    {
      id: 1,
      amount: 1000000,
      description: "Khoản vay mua nhà",
      interest_rate: 5.5,
      due_date: "2024-06-01",
      monthly_payment: 5000000,
      category: "Vay mua nhà",
      user_id: 1,
      is_paid: false,
      created_at: "2023-01-15T00:00:00Z",
      updated_at: "2023-01-15T00:00:00Z"
    },
    {
      id: 2,
      amount: 500000,
      description: "Vay tiêu dùng",
      interest_rate: 10.5,
      due_date: "2024-03-01",
      monthly_payment: 100000,
      category: "Vay tiêu dùng",
      user_id: 1,
      is_paid: false,
      created_at: "2023-02-15T00:00:00Z",
      updated_at: "2023-02-15T00:00:00Z"
    }
  ],
  total: 2,
  pages: 1,
  current_page: 1
};

export const MOCK_DEBT_STATISTICS = {
  total_debt: 1500000,
  upcoming_debts: [
    {
      date: "2024-03-01",
      total: 500000
    },
    {
      date: "2024-06-01",
      total: 1000000
    }
  ]
};

// Expense related mock data
export const MOCK_EXPENSE = {
  amount: 500000,
  description: "Mua sắm tại siêu thị",
  category: "Mua sắm",
  date: "2023-11-15"
};

export const MOCK_EXPENSES_RESPONSE = {
  items: [
    {
      id: 1,
      amount: 500000,
      description: "Tiền ăn hàng tuần",
      category: "Thực phẩm",
      date: "2024-01-15",
      user_id: 1,
      created_at: "2024-01-15T00:00:00Z",
      updated_at: "2024-01-15T00:00:00Z"
    },
    {
      id: 2,
      amount: 300000,
      description: "Tiền xăng xe",
      category: "Đi lại",
      date: "2024-01-20",
      user_id: 1,
      created_at: "2024-01-20T00:00:00Z",
      updated_at: "2024-01-20T00:00:00Z"
    }
  ],
  total: 2,
  pages: 1,
  current_page: 1
};

export const MOCK_EXPENSE_STATISTICS = {
  total_expenses: 800000,
  by_category: [
    {
      category: "Thực phẩm",
      total: 500000
    },
    {
      category: "Đi lại",
      total: 300000
    }
  ],
  monthly_expenses: [
    {
      date: "2024-01-15",
      total: 500000
    },
    {
      date: "2024-01-20",
      total: 300000
    }
  ]
};

// Income related mock data
export const MOCK_INCOME = {
  amount: 10000000,
  description: "Lương tháng",
  source: "Công ty ABC",
  date: new Date().toISOString().split('T')[0]
};

export const MOCK_INCOMES_RESPONSE = {
  items: [
    {
      id: 1,
      amount: 10000000,
      description: "Lương tháng",
      source: "Công ty ABC",
      date: "2024-01-01",
      user_id: 1,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z"
    },
    {
      id: 2,
      amount: 2000000,
      description: "Tiền thưởng",
      source: "Công ty ABC",
      date: "2024-01-05",
      user_id: 1,
      created_at: "2024-01-05T00:00:00Z",
      updated_at: "2024-01-05T00:00:00Z"
    }
  ],
  total: 2,
  pages: 1,
  current_page: 1
};

export const MOCK_INCOME_STATISTICS = {
  total_income: 12000000,
  by_source: [
    {
      source: "Công ty ABC",
      total: 12000000
    }
  ],
  monthly_income: [
    {
      date: "2024-01-01",
      total: 10000000
    },
    {
      date: "2024-01-05",
      total: 2000000
    }
  ]
};

// Summary related mock data
export const MOCK_SUMMARIES_RESPONSE = {
  items: [
    {
      id: 1,
      user_id: 1,
      date: "2024-01-31",
      total_income: 12000000,
      total_expense: 800000,
      total_debt: 1500000,
      balance: 11200000,
      created_at: "2024-01-31T00:00:00Z",
      updated_at: "2024-01-31T00:00:00Z"
    }
  ],
  total: 1,
  pages: 1,
  current_page: 1
};

export const MOCK_CURRENT_SUMMARY = {
  id: 1,
  user_id: 1,
  date: new Date().toISOString().split('T')[0],
  total_income: 12000000,
  total_expense: 800000,
  total_debt: 1500000,
  balance: 11200000,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

export const MOCK_SUMMARY_STATISTICS = {
  daily_summaries: [
    {
      date: "2024-01-01",
      total_income: 10000000,
      total_expense: 0,
      total_debt: 1500000,
      balance: 10000000
    },
    {
      date: "2024-01-05",
      total_income: 2000000,
      total_expense: 0,
      total_debt: 1500000,
      balance: 2000000
    },
    {
      date: "2024-01-15",
      total_income: 0,
      total_expense: 500000,
      total_debt: 1500000,
      balance: -500000
    },
    {
      date: "2024-01-20",
      total_income: 0,
      total_expense: 300000,
      total_debt: 1500000,
      balance: -300000
    }
  ]
};

// Prediction related mock data
export const MOCK_TRAIN_MODEL_RESPONSE = {
  success: true,
  message: "Model trained successfully"
};

export const MOCK_PREDICT_EXPENSES_REQUEST = {
  income: 15000000
};

export const MOCK_PREDICT_EXPENSES_RESPONSE = {
  success: true,
  predicted_expenses: 900000,
  income: 15000000,
  savings_potential: 14100000,
  insights_available: true,
  insights: [
    {
      category: "Thực phẩm",
      avg_percentage: 0.05,
      suggestion: "Bạn đang chi tiêu hợp lý cho thực phẩm."
    },
    {
      category: "Đi lại",
      avg_percentage: 0.025,
      suggestion: "Bạn có thể tiết kiệm thêm bằng cách sử dụng phương tiện công cộng."
    }
  ]
};

export const MOCK_INSIGHTS_RESPONSE = {
  success: true,
  insights: [
    {
      id: 1,
      user_id: 1,
      income_range: "10000000-20000000",
      category: "Thực phẩm",
      avg_percentage: 0.05,
      created_at: "2024-01-31T00:00:00Z",
      updated_at: "2024-01-31T00:00:00Z"
    },
    {
      id: 2,
      user_id: 1,
      income_range: "10000000-20000000",
      category: "Đi lại",
      avg_percentage: 0.025,
      created_at: "2024-01-31T00:00:00Z",
      updated_at: "2024-01-31T00:00:00Z"
    }
  ]
}; 