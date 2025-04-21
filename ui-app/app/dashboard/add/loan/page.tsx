"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, AlertCircle } from "lucide-react";
import {
  useCreateExpense,
  useExpenseCategories,
} from "@/reactquery/hook/expenses";
import { ExpenseCategory } from "@/services/expenses";
import { toast } from "sonner";

type FormErrors = {
  amount?: string;
  description?: string;
  category_id?: string;
  date?: string;
};

type FormField = "amount" | "description" | "category_id" | "date";

export default function AddExpensePage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    amount: "",
    description: "",
    category_id: "",
    date: new Date().toISOString().substring(0, 10),
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [apiError, setApiError] = useState<string | null>(null);

  const { mutate: createExpense, isPending } = useCreateExpense();
  const {
    data: categoriesData,
    isLoading: categoriesLoading,
    isError: categoriesError,
  } = useExpenseCategories();

  const categories = categoriesData?.data || [];

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    const fieldName = name as FormField;

    setFormData((prev) => ({ ...prev, [fieldName]: value }));

    if (fieldName in errors) {
      setErrors((prev) => ({ ...prev, [fieldName]: undefined }));
    }

    if (apiError) {
      setApiError(null);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.amount) {
      newErrors.amount = "Vui lòng nhập số tiền";
    } else if (parseFloat(formData.amount) <= 0) {
      newErrors.amount = "Số tiền phải lớn hơn 0";
    }

    if (!formData.description.trim()) {
      newErrors.description = "Vui lòng nhập mô tả";
    } else if (formData.description.trim().length < 3) {
      newErrors.description = "Mô tả phải có ít nhất 3 ký tự";
    }

    if (!formData.category_id) {
      newErrors.category_id = "Vui lòng chọn loại chi tiêu";
    }

    if (!formData.date) {
      newErrors.date = "Vui lòng chọn ngày";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const formatDateForAPI = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toISOString().split("T")[0];
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const payload = {
      ...formData,
      amount: parseFloat(formData.amount),
      category_id: parseInt(formData.category_id),
      date: formatDateForAPI(formData.date),
    };

    createExpense(payload, {
      onSuccess: () => {
        toast("thành công");
      },
      onError: (error: unknown) => {
        console.error("Expense creation error:", error);
        const errorMessage =
          error instanceof Error
            ? error.message
            : "Có lỗi xảy ra khi tạo chi tiêu. Vui lòng thử lại.";
        setApiError(errorMessage);
      },
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
              <CardTitle>Thêm chi tiêu mới</CardTitle>
              <CardDescription>
                Thêm khoản chi tiêu mới vào hệ thống
              </CardDescription>
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

          {categoriesError && (
            <div className="bg-amber-50 p-3 rounded-md border border-amber-200 flex items-start">
              <AlertCircle className="h-5 w-5 text-amber-500 mr-2 mt-0.5" />
              <span className="text-amber-600 text-sm">
                Không thể tải danh mục chi tiêu. Vui lòng làm mới trang.
              </span>
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
            <Label htmlFor="description">Mô tả</Label>
            <Input
              id="description"
              name="description"
              placeholder="Mô tả chi tiết"
              value={formData.description}
              onChange={handleChange}
              className={errors.description ? "border-red-300" : ""}
              required
            />
            {errors.description && (
              <p className="text-red-500 text-xs mt-1">{errors.description}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="category_id">Loại chi tiêu</Label>
            <select
              id="category_id"
              name="category_id"
              className={`w-full flex h-9 rounded-md border ${
                errors.category_id ? "border-red-300" : "border-input"
              } bg-transparent px-3 py-1 text-sm shadow-sm`}
              value={formData.category_id}
              onChange={handleChange}
              required
              disabled={categoriesLoading}
            >
              <option value="">Chọn loại chi tiêu</option>
              {categories.map((category: ExpenseCategory) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            {errors.category_id && (
              <p className="text-red-500 text-xs mt-1">{errors.category_id}</p>
            )}
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
          <Button
            type="submit"
            className="w-full"
            disabled={isPending || categoriesLoading || categoriesError}
          >
            {isPending ? "Đang lưu..." : "Lưu chi tiêu"}
          </Button>
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={() => router.back()}
          >
            Hủy
          </Button>
        </CardFooter>
      </Card>
    </form>
  );
}
