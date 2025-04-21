import React, { useForm } from 'react';
import { Select, DateInput, Group } from '@mantine/core';

export interface ExpenseFormField {
  amount: number;
  description: string;
  category: string;
  date: string;
}

const ExpenseForm: React.FC<{ expense?: ExpenseFormField }> = ({ expense }) => {
  const form = useForm<ExpenseFormField>({
    initialValues: {
      amount: expense?.amount ?? 0,
      description: expense?.description ?? '',
      category: expense?.category ?? '',
      date: expense?.date ?? new Date().toISOString().split('T')[0]
    },
  });

  const categories = ['Food', 'Transportation', 'Housing', 'Entertainment'];

  return (
    <form>
      <Select
        label="Loại chi tiêu"
        placeholder="Chọn loại chi tiêu"
        data={categories}
        {...form.getInputProps('category')}
        required
      />

      <DateInput
        valueFormat="YYYY-MM-DD"
        label="Ngày chi tiêu"
        placeholder="Chọn ngày"
        {...form.getInputProps('date')}
        required
      />
      
      <Group justify="flex-end" mt="md">
      </Group>
    </form>
  );
};

export default ExpenseForm; 