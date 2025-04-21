import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "file:text-[#111827] placeholder:text-[#6B7280] selection:bg-[#1BA784] selection:text-white dark:bg-[#202020]/30 border-[#E5E7EB] flex h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm dark:file:text-white dark:placeholder:text-[#9CA3AF] dark:selection:bg-[#1BA784] dark:selection:text-white dark:dark:bg-[#202020]/30 dark:border-[#202020]",
        "focus-visible:border-[#1BA784] focus-visible:ring-[#1BA784]/50 focus-visible:ring-[3px] dark:focus-visible:border-[#1BA784] dark:focus-visible:ring-[#1BA784]/50",
        "aria-invalid:ring-red-500/20 dark:aria-invalid:ring-red-500/40 aria-invalid:border-red-500 dark:aria-invalid:ring-red-900/20 dark:dark:aria-invalid:ring-red-900/40 dark:aria-invalid:border-red-900",
        className
      )}
      {...props}
    />
  )
}

export { Input }
