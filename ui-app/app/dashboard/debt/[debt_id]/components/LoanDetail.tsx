import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

type LoanData = {
  amount: number;
  category: string | null;
  created_at: string;
  description: string;
  due_date: string;
  id: number;
  interest_rate: number;
  is_paid: boolean;
  monthly_payment: number | null;
  updated_at: string;
  user_id: number;
};

export default function LoanDetail({ data }: { data: LoanData }) {
  return (
    <Card className="w-full mx-auto mt-10">
      <CardHeader>
        <CardTitle>Chi tiết khoản vay</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm text-muted-foreground">
        <div>
          <span className="font-medium text-black">ID:</span> {data.id}
        </div>
        <div>
          <span className="font-medium text-black">Người dùng:</span>{" "}
          {data.user_id}
        </div>
        <div>
          <span className="font-medium text-black">Số tiền vay:</span>{" "}
          {data.amount.toLocaleString()} VND
        </div>
        <div>
          <span className="font-medium text-black">Lãi suất:</span>{" "}
          {data.interest_rate}%
        </div>
        <div>
          <span className="font-medium text-black">Mô tả:</span>{" "}
          {data.description}
        </div>
        <div>
          <span className="font-medium text-black">Ngày tạo:</span>{" "}
          {new Date(data.created_at).toLocaleString()}
        </div>
        <div>
          <span className="font-medium text-black">Đến hạn:</span>{" "}
          {new Date(data.due_date).toLocaleDateString()}
        </div>
        <div>
          <span className="font-medium text-black">Trạng thái:</span>{" "}
          <Badge variant={data.is_paid ? "default" : "destructive"}>
            {data.is_paid ? "Đã thanh toán" : "Chưa thanh toán"}
          </Badge>
        </div>
        <div>
          <span className="font-medium text-black">Danh mục:</span>{" "}
          {data.category ?? "Không có"}
        </div>
        <div>
          <span className="font-medium text-black">Thanh toán hàng tháng:</span>{" "}
          {data.monthly_payment
            ? `${data.monthly_payment.toLocaleString()} VND`
            : "Chưa có"}
        </div>
        <div>
          <span className="font-medium text-black">Cập nhật lần cuối:</span>{" "}
          {new Date(data.updated_at).toLocaleString()}
        </div>

        {!data.is_paid && (
          <Button variant="outline" className="mt-4">
            Đánh dấu là đã thanh toán
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
