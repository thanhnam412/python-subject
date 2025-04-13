"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "./ui/checkbox";

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const onGet = async () => {
    try {
      const data = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          password: "12345",
          username: "string",
        }),
      });
      if (data.ok) {
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
          <button onClick={() => onGet()}>CLick</button>
          <form action={() => console.log(1)}>
            <div className="grid gap-6">
              <div className="grid gap-6">
                <div className="grid gap-3">
                  <Label htmlFor="username">Tên đăng nhập</Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="m@example.com"
                    required
                  />
                </div>
                <div className="grid gap-3">
                  <Label htmlFor="password">Mật khẩu</Label>
                  <Input id="password" type="password" required />
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="terms" />
                  <Label htmlFor="terms">Keep me signed in</Label>
                </div>

                <Button type="submit" className="w-full">
                  Login
                </Button>
              </div>
              <div className="text-center text-sm">
                Nếu bạn chưa có tài khoảng{" "}
                <a href="#" className="underline underline-offset-4">
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
