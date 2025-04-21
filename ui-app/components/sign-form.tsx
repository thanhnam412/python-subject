"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useRegister } from "@/reactquery/hook/auth";
import { toast } from "sonner";

export function SignUpForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [data, setData] = useState<{
    username: string;
    password: string;
    email: string;
  }>({
    username: "",
    password: "",
    email: "",
  });
  const { mutateAsync: register } = useRegister();
  const auth = useAuth();

  const handleLogin = async () => {
    if (auth) {
      return;
    }
    try {
      const result = await register(data);
      if (result.data) {
        window.location.href = "/";
      }
    } catch (error) {
      console.log(error);
      toast("Đăng kí không thành công.", {
        style: { background: "#fb2c36", color: "white" },
      });
    }
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <p className="text-center text-[32px] text-[#299D91] font-bold">
        Tạo tài khoản
      </p>
      <Card>
        <CardContent>
          <form action={() => {}}>
            <div className="grid gap-6">
              <div className="grid gap-6">
                <div className="grid gap-3">
                  <Label htmlFor="username">Tên</Label>
                  <Input
                    onChange={(e) =>
                      setData({ ...data, username: e.target.value })
                    }
                    id="username"
                    type="text"
                    placeholder="username"
                    required
                  />
                </div>
                <div className="grid gap-3">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    onChange={(e) =>
                      setData({ ...data, email: e.target.value })
                    }
                    id="email"
                    type="email"
                    placeholder="exam@mail.com"
                    required
                  />
                </div>
                <div className="grid gap-3">
                  <Label htmlFor="password">Mật khẩu</Label>
                  <Input
                    id="password"
                    type="password"
                    required
                    onChange={(e) =>
                      setData({ ...data, password: e.target.value })
                    }
                  />
                </div>

                <Button type="submit" onClick={handleLogin} className="w-full">
                  Đăng ký
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
