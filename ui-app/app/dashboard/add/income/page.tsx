"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, AlertCircle } from "lucide-react";
import { useCreateIncome } from "@/reactquery/hook/incomes";

type FormErrors = {
  amount?: string;
  source?: string;
  date?: string;
};

type FormField = 'amount' | 'source' | 'description' | 'date';

export default function AddIncomePage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    amount: "",
    source: "",
    description: "",
    date: new Date().toISOString().substring(0, 10),
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [apiError, setApiError] = useState<string | null>(null);

  const { mutate: createIncome, isPending } = useCreateIncome();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const fieldName = name as FormField;
    
    setFormData((prev) => ({ ...prev, [fieldName]: value }));
    
    // Clear error when field is edited
    if (fieldName in errors) {
      setErrors(prev => ({ ...prev, [fieldName]: undefined }));
    }
    
    // Clear API error when any field is changed
    if (apiError) {
      setApiError(null);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    // Validate amount
    if (!formData.amount) {
      newErrors.amount = "Vui lòng nhập số tiền";
    } else if (parseFloat(formData.amount) <= 0) {
      newErrors.amount = "Số tiền phải lớn hơn 0";
    }
    
    // Validate source
    if (!formData.source.trim()) {
      newErrors.source = "Vui lòng nhập nguồn thu";
    } else if (formData.source.trim().length < 3) {
      newErrors.source = "Nguồn thu phải có ít nhất 3 ký tự";
    }
    
    // Validate date
    if (!formData.date) {
      newErrors.date = "Vui lòng chọn ngày";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const formatDateForAPI = (dateString: string): string => {
    // Đảm bảo định dạng ngày tháng chuẩn cho API
    // Chuyển từ YYYY-MM-DD thành chuỗi ISO với thời gian là 00:00:00 tại múi giờ UTC
    const date = new Date(dateString);
    return date.toISOString().split('T')[0]; // Lấy chỉ phần ngày YYYY-MM-DD
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    const payload = {
      ...formData,
      amount: parseFloat(formData.amount),
      date: formatDateForAPI(formData.date),
    };
    
    createIncome(payload, {
      onSuccess: () => {
        router.push("/dashboard/overview");
      },
      onError: (error: unknown) => {
        console.error("Income creation error:", error);
        const errorMessage = error instanceof Error 
          ? error.message 
          : "Có lỗi xảy ra khi tạo thu nhập. Vui lòng thử lại.";
        setApiError(errorMessage);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardHeader>
          <div className="flex items-center">
            <Button 
              type="button" 
              variant="ghost" 
              size="sm" 
              className="mr-2"
              onClick={() => router.back()}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <CardTitle>Thêm thu nhập mới</CardTitle>
              <CardDescription>Thêm khoản thu nhập mới vào hệ thống</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {apiError && (
            <div className="bg-red-50 p-3 rounded-md border border-red-200 flex items-start">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2 mt-0.5" />
              <span className="text-red-600 text-sm">{apiError}</span>
            </div>
          )}
        
          <div className="space-y-2">
            <Label htmlFor="amount">Số tiền</Label>
            <Input
              id="amount"
              name="amount"
              type="number"
              placeholder="Nhập số tiền"
              value={formData.amount}
              onChange={handleChange}
              className={errors.amount ? "border-red-300" : ""}
              required
            />
            {errors.amount && (
              <p className="text-red-500 text-xs mt-1">{errors.amount}</p>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="source">Nguồn thu</Label>
            <Input
              id="source"
              name="source"
              placeholder="Ví dụ: Lương, thưởng, đầu tư..."
              value={formData.source}
              onChange={handleChange}
              className={errors.source ? "border-red-300" : ""}
              required
            />
            {errors.source && (
              <p className="text-red-500 text-xs mt-1">{errors.source}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Mô tả (không bắt buộc)</Label>
            <Input
              id="description"
              name="description"
              placeholder="Mô tả chi tiết"
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="date">Ngày</Label>
            <Input
              id="date"
              name="date"
              type="date"
              value={formData.date}
              onChange={handleChange}
              className={errors.date ? "border-red-300" : ""}
              required
            />
            {errors.date && (
              <p className="text-red-500 text-xs mt-1">{errors.date}</p>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex flex-col gap-4">
          <Button type="submit" className="w-full" disabled={isPending}>
            {isPending ? "Đang lưu..." : "Lưu thu nhập"}
          </Button>
          <Button type="button" variant="outline" className="w-full" onClick={() => router.back()}>
            Hủy
          </Button>
        </CardFooter>
      </Card>
    </form>
  );
} 