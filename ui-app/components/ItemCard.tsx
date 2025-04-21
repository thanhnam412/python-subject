import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Clock } from "lucide-react";
import { useRouter } from "next/navigation";

interface Props {
  item: {
    id: number;
    description: string;
    amount: number;
    due_date: string;
    interest_rate: number;
    is_paid: boolean;
  };
}

export function ItemCard({ item }: Props) {
  const router = useRouter();

  const handleClick = () => {
    router.push(`/dashboard/debt/${item.id.toString()}`);
  };

  return (
    <Card className="w-full shadow-md hover:cursor-pointer hover:bg-primary/10 duration-100" onClick={handleClick}>
      <CardHeader className="flex flex-row justify-between items-center">
        <CardTitle className="text-base">{item.description}</CardTitle>
        <Badge variant={item.is_paid ? "default" : "destructive"}>
          {item.is_paid ? (
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4" /> Đã thanh toán
            </span>
          ) : (
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" /> Chưa thanh toán
            </span>
          )}
        </Badge>
      </CardHeader>
      <CardContent className="text-sm space-y-1">
        <p>
          <strong>Số tiền:</strong> {item.amount.toLocaleString()}₫
        </p>
        <p>
          <strong>Ngày đáo hạn:</strong>{" "}
          {new Date(item.due_date).toLocaleDateString()}
        </p>
        <p>
          <strong>Lãi suất:</strong> {item.interest_rate}%
        </p>
      </CardContent>
    </Card>
  );
}
