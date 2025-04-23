"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { useCreateExpense } from "@/reactquery/hook/expenses";
import { toast } from "sonner";

const FormSchema = z.object({
  date: z.date().optional(),
  amount: z.coerce.number(),
  title: z.string(),
  description: z.string().optional(),
});
export default function CalendarForm() {
  const { mutateAsync } = useCreateExpense();

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });

  const onSubmit = async (data: z.infer<typeof FormSchema>) => {
    try {
      const resutl = await mutateAsync(data);
      console.log(resutl);
      toast("Thành công", { style: { background: "#22c55e", color: "white" } });
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <Card className="p-[16px] mt-[32px]">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-[32px]">
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormLabel>Tên chi tiêu</FormLabel>
                <Input placeholder="A" type="text" onChange={field.onChange} />
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="amount"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormLabel>Số tiền</FormLabel>
                <Input
                  placeholder="100000"
                  type="number"
                  onChange={field.onChange}
                />
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormLabel>Miêu tả</FormLabel>
                <Input
                  placeholder="abc"
                  type="text"
                  onChange={field.onChange}
                />
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="date"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormLabel>Ngày</FormLabel>
                <Popover>
                  <PopoverTrigger asChild>
                    <FormControl>
                      <Button
                        variant={"outline"}
                        className={cn(
                          "w-[240px] pl-3 text-left font-normal",
                          !field.value && "text-muted-foreground"
                        )}
                      >
                        {field.value ? (
                          format(field.value, "PPP")
                        ) : (
                          <span>Chọn ngày</span>
                        )}
                        <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                      </Button>
                    </FormControl>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      onSelect={field.onChange}
                      disabled={(date) =>
                        date > new Date() || date < new Date("1900-01-01")
                      }
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit">Thêm</Button>
        </form>
      </Form>
    </Card>
  );
}
