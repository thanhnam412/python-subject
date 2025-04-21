import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-[#111827] focus-visible:ring-[#111827]/50 focus-visible:ring-[3px] aria-invalid:ring-red-500/20 dark:aria-invalid:ring-red-500/40 aria-invalid:border-red-500 dark:focus-visible:border-[#E5E7EB] dark:focus-visible:ring-[#E5E7EB]/50 dark:aria-invalid:ring-red-900/20 dark:dark:aria-invalid:ring-red-900/40 dark:aria-invalid:border-red-900",
  {
    variants: {
      variant: {
        default:
          "bg-[#1BA784] text-white shadow-xs hover:bg-[#1BA784]/90 dark:bg-[#1BA784] dark:text-white dark:hover:bg-[#1BA784]/90",
        destructive:
          "bg-red-500 text-white shadow-xs hover:bg-red-500/90 focus-visible:ring-red-500/20 dark:focus-visible:ring-red-500/40 dark:bg-red-500/60 dark:bg-red-900 dark:hover:bg-red-900/90 dark:focus-visible:ring-red-900/20 dark:dark:focus-visible:ring-red-900/40 dark:dark:bg-red-900/60",
        outline:
          "border border-[#E5E7EB] bg-white shadow-xs hover:bg-[#F9FAFB] hover:text-[#111827] dark:bg-[#1E1E1E] dark:border-[#6B7280] dark:hover:bg-[#202020] dark:hover:text-white dark:text-[#9CA3AF]",
        secondary:
          "bg-[#F9FAFB] text-[#111827] shadow-xs hover:bg-[#F9FAFB]/80 dark:bg-[#202020] dark:text-white dark:hover:bg-[#202020]/80",
        ghost:
          "hover:bg-[#F9FAFB] hover:text-[#111827] dark:hover:bg-[#202020] dark:hover:text-white dark:text-[#9CA3AF]",
        link: "text-[#1BA784] underline-offset-4 hover:underline dark:text-[#1BA784]",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
