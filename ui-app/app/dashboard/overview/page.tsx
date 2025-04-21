"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, CreditCard, TrendingDown, Wallet, RefreshCw } from "lucide-react";
import { useCurrentSummary, useSummaryStatistics } from "@/reactquery/hook/summary";
import { FinancialChart } from "@/components/FinancialChart";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function OverviewPage() {
  const [period, setPeriod] = useState<"week" | "month" | "year">("month");
  const [refreshKey, setRefreshKey] = useState(0);
  
  const { 
    data: summaryData, 
    isLoading: summaryLoading, 
    isError: summaryError,
    refetch: refetchSummary 
  } = useCurrentSummary();
  
  const { 
    data: statisticsData, 
    isLoading: statsLoading,
    isError: statsError,
    refetch: refetchStats
  } = useSummaryStatistics(period);

  const handleRefresh = () => {
    refetchSummary();
    refetchStats();
    setRefreshKey(prev => prev + 1);
  };

  const handlePeriodChange = (newPeriod: "week" | "month" | "year") => {
    setPeriod(newPeriod);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Tổng quan tài chính</h1>
        <Button variant="outline" size="sm" onClick={handleRefresh}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Làm mới
        </Button>
      </div>

      {/* Financial summary cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Số dư hiện tại
            </CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {summaryError ? (
              <div className="text-red-500 text-sm">Lỗi tải dữ liệu</div>
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {summaryLoading ? "Đang tải..." : `₫${summaryData?.data?.balance?.toLocaleString() || 0}`}
                </div>
                <p className="text-xs text-muted-foreground">
                  Tiền còn lại sau khi trừ chi phí
                </p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Tổng thu nhập
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {summaryError ? (
              <div className="text-red-500 text-sm">Lỗi tải dữ liệu</div>
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {summaryLoading ? "Đang tải..." : `₫${summaryData?.data?.total_income?.toLocaleString() || 0}`}
                </div>
                <p className="text-xs text-muted-foreground">
                  Thu nhập trong tháng
                </p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Tổng chi tiêu
            </CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {summaryError ? (
              <div className="text-red-500 text-sm">Lỗi tải dữ liệu</div>
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {summaryLoading ? "Đang tải..." : `₫${summaryData?.data?.total_expense?.toLocaleString() || 0}`}
                </div>
                <p className="text-xs text-muted-foreground">
                  Chi tiêu trong tháng
                </p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Tổng nợ
            </CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {summaryError ? (
              <div className="text-red-500 text-sm">Lỗi tải dữ liệu</div>
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {summaryLoading ? "Đang tải..." : `₫${summaryData?.data?.total_debt?.toLocaleString() || 0}`}
                </div>
                <p className="text-xs text-muted-foreground">
                  Tổng số nợ cần trả
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Chart area */}
      <Card className="col-span-4">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Thống kê theo {period === 'month' ? 'tháng' : period === 'year' ? 'năm' : 'tuần'}</CardTitle>
              <CardDescription>
                Tóm tắt thu nhập, chi tiêu và nợ theo thời gian
              </CardDescription>
            </div>
            <div className="flex space-x-2">
              <Button 
                variant={period === "week" ? "default" : "outline"} 
                size="sm"
                onClick={() => handlePeriodChange("week")}
              >
                Tuần
              </Button>
              <Button 
                variant={period === "month" ? "default" : "outline"} 
                size="sm"
                onClick={() => handlePeriodChange("month")}
              >
                Tháng
              </Button>
              <Button 
                variant={period === "year" ? "default" : "outline"} 
                size="sm"
                onClick={() => handlePeriodChange("year")}
              >
                Năm
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pl-2">
          {statsError ? (
            <div className="flex items-center justify-center h-[350px] text-red-500">
              <p>Lỗi tải dữ liệu biểu đồ. Vui lòng thử lại sau.</p>
            </div>
          ) : statsLoading ? (
            <div className="flex items-center justify-center h-[350px]">
              <p>Đang tải dữ liệu thống kê...</p>
            </div>
          ) : (
            <div className="h-[350px] w-full">
              <FinancialChart 
                key={refreshKey}
                data={statisticsData?.data?.daily_summaries || []} 
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 