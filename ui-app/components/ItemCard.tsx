import { Card, CardTitle } from "@/components/ui/card";

interface DebtCardProps {
  item: {
    id: number;
    title: string;
    description: string;
    amount: number;
    due_date: string;
    interest_rate: number;
  };
}

export function ItemDebtCard({ item }: DebtCardProps) {
  return (
    <Card className="w-full shadow-md mb-4">
      <div className="px-[24px]">
        <CardTitle className="text-base">Tên khoản nợ: {item.title}</CardTitle>
        <CardTitle className="text-base">Miêu tả: {item.description}</CardTitle>
        <CardTitle className="text-base flex flex-nowrap gap-[4px]">
          Số tiền nợ: <p className="text-red-500">{item.amount}</p>
        </CardTitle>
        <CardTitle className="text-base">
          Ngày đáo hạn: {item.due_date}
        </CardTitle>
        <CardTitle className="text-base">Id: {item.id}</CardTitle>
        <CardTitle className="text-base">
          Lãi suất: {item.interest_rate}%
        </CardTitle>
      </div>
    </Card>
  );
}

interface IncomeCard {
  item: {
    id: number;
    amount: number;
    date: string;
    source: string;
  };
}

export function ItemIncomeCard({ item }: IncomeCard) {
  return (
    <Card className="w-full shadow-md">
      <div className="px-[24px]">
        <CardTitle className="text-base">Nguồn: {item.source}</CardTitle>
        <CardTitle className="text-base flex flex-nowrap gap-[4px]">
          Số tiền: <p className="text-green-500">{item.amount}</p>
        </CardTitle>
        <CardTitle className="text-base">Ngày nhận: {item.date}</CardTitle>
        <CardTitle className="text-base">Id: {item.id}</CardTitle>
      </div>
    </Card>
  );
}

interface ExpenseCard {
  item: {
    id: number;
    title: string;
    description: string;
    amount: number;
    date: string;
  };
}

export function ItemExpenseCard({ item }: ExpenseCard) {
  return (
    <Card className="w-full shadow-md">
      <div className="px-[24px]">
        <CardTitle className="text-base">Tên: {item.title}</CardTitle>
        <CardTitle className="text-base">Miêu tả: {item.description}</CardTitle>
        <CardTitle className="text-base flex flex-nowrap gap-[4px]">
          Số tiền: <p className="text-red-500">{item.amount}</p>
        </CardTitle>
        <CardTitle className="text-base">Ngày chi: {item.date}</CardTitle>
        <CardTitle className="text-base">Id: {item.id}</CardTitle>
      </div>
    </Card>
  );
}
