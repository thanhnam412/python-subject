"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import Link from "next/link";

export default function AddPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Thêm mới</CardTitle>
        <CardDescription>
          Thêm thu nhập, chi tiêu hoặc khoản nợ mới
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Link href="/dashboard/add/income">
              <Button className="w-full">
                <Plus className="mr-2 h-4 w-4" /> Thu nhập
              </Button>
            </Link>
            <Link href="/dashboard/add/expense">
              <Button className="w-full">
                <Plus className="mr-2 h-4 w-4" /> Chi tiêu
              </Button>
            </Link>
            <Link href="/dashboard/add/debt">
              <Button className="w-full">
                <Plus className="mr-2 h-4 w-4" /> Khoản nợ
              </Button>
            </Link>
          </div>
          <div className="h-[200px] rounded-md border border-dashed flex items-center justify-center">
            <p className="text-muted-foreground">Chọn loại mục để thêm mới</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
} 