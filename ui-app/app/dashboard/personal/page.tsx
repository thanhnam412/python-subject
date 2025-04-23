"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useDebts } from "@/reactquery/hook/debts";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { ItemDebtCard, ItemExpenseCard, ItemIncomeCard } from "@/components/ItemCard";
import { PaginationControls } from "@/components/PaginationControls";
import { useState } from "react";
import { useExpenses } from "@/reactquery/hook/expenses";
import { useIncomes } from "@/reactquery/hook/incomes";

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}

export default function PersonalPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState("income");

  const hook = (() => {
    switch (selectedCategory) {
      case "expense":
        return useExpenses;
      case "income":
        return useIncomes;
      case "debts":
      default:
        return useDebts;
    }
  })();

  const { data: res } = hook({ page: currentPage });
  const { data } = res || {};

  const renderNoneData = () => (
    <div className="h-full w-full flex justify-center items-center">
      không có dữ liệu
    </div>
  );

  return (
    <Card className="h-full mt-[32px]">
      <CardHeader>
        <CardTitle>Personal</CardTitle>
      </CardHeader>
      <CardContent className="h-full">
        <Tabs
          className="h-full"
          defaultValue="income"
          onValueChange={(val) => {
            setSelectedCategory(val);
            setCurrentPage(1);
          }}
        >
          <TabsList>
            <TabsTrigger value="income">Thu Nhập</TabsTrigger>
            <TabsTrigger value="expense">Chi tiêu</TabsTrigger>
            <TabsTrigger value="debts">Khoản nợ</TabsTrigger>
          </TabsList>

          <TabsContent
            value="income"
            className="h-[calc(100%-80px)] flex flex-col justify-between"
          >
            {!data || !Array.isArray(data.items) || data.items.length === 0 ? (
              renderNoneData()
            ) : (
              <>
                 <div className="grid grid-cols-3 gap-[12px]">
                  {data.items.map((item: any) => (
                    <ItemIncomeCard key={item.id} item={item} />
                  ))}
                </div>
                <PaginationControls
                  currentPage={data?.current_page ?? 1}
                  totalPages={data?.pages}
                  onPageChange={setCurrentPage}
                />
              </>
            )}
          </TabsContent>

          <TabsContent
            value="expense"
            className="h-[calc(100%-80px)] flex flex-col justify-between"
          >
            {!data || !Array.isArray(data.items) || data.items.length === 0 ? (
              renderNoneData()
            ) : (
              <>
                <div className="grid grid-cols-3 gap-[12px]">
                  {data.items.map((item: any) => (
                    <ItemExpenseCard key={item.id} item={item} />
                  ))}
                </div>
                <PaginationControls
                  currentPage={data?.current_page}
                  totalPages={data?.pages}
                  onPageChange={setCurrentPage}
                />
              </>
            )}
          </TabsContent>

          <TabsContent
            value="debts"
            className="h-[calc(100%-80px)] flex flex-col justify-between"
          >
            {!data || !Array.isArray(data.items) || data.items.length === 0 ? (
              renderNoneData()
            ) : (
              <>
                <div className="grid grid-cols-3 gap-[12px]">
                  {data.items.map((item: any) => (
                    <ItemDebtCard key={item.id} item={item} />
                  ))}
                </div>
                <PaginationControls
                  currentPage={data?.current_page}
                  totalPages={data?.pages}
                  onPageChange={setCurrentPage}
                />
              </>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
