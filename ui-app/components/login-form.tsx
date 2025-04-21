"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useLogin } from "@/reactquery/hook/auth";

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [data, setData] = useState<{ username: string; password: string }>({
    username: "",
    password: "",
  });
  const { mutateAsync: login } = useLogin();
  const auth = useAuth();

  const handleLogin = async () => {
    if (auth) {
      return;
    }
    try {
      const result = await login(data);
      if (result.data) {
        window.location.href = "/";
      }
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <p className="text-center text-[32px] text-[#299D91] font-bold">
        Đăng nhập
      </p>
      <Card>
        <CardContent>
          <form action={() => {}}>
            <div className="grid gap-6">
              <div className="grid gap-6">
                <div className="grid gap-3">
                  <Label htmlFor="username">Tên đăng nhập</Label>
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
                  Login
                </Button>
              </div>
              <div className="text-center text-sm">
                Nếu bạn chưa có tài khoảng{" "}
                <a href="/signup" className="underline underline-offset-4">
                  Đăng ký
                </a>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
