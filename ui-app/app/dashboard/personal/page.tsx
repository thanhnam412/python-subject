"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useDebts } from "@/reactquery/hook/debts";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { ItemCard } from "@/components/ItemCard";
import { PaginationControls } from "@/components/PaginationControls";
import { useState } from "react";

export default function PersonalPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState("debts");
  const hook = (() => {
    switch (selectedCategory) {
      case "expense":
        return useDebts;
      case "income":
        return useDebts;
      case "debts":
        return useDebts;

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
          defaultValue="debts"
          onValueChange={setSelectedCategory}
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
            {!data || data?.items?.length === 0 ? (
              renderNoneData()
            ) : (
              <div>1</div>
            )}
          </TabsContent>
          <TabsContent
            value="expense"
            className="h-[calc(100%-80px)] flex flex-col justify-between"
          >
            {!data || data?.items?.length === 0 ? (
              renderNoneData()
            ) : (
              <div>1</div>
            )}
          </TabsContent>
          <TabsContent
            value="debts"
            className="h-[calc(100%-80px)] flex flex-col justify-between"
          >
            {!data || data?.items?.length === 0 ? (
              renderNoneData()
            ) : (
              <>
                <div className="grid grid-cols-3 gap-[12px]">
                  {data.items.map((item: any) => (
                    <ItemCard key={item.id} item={item} />
                  ))}
                </div>
                <PaginationControls
                  currentPage={data.current_page}
                  totalPages={data.pages}
                  onPageChange={(page) => {
                    setCurrentPage(page);
                  }}
                />
              </>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
