import { cn } from "@/lib/utils"

function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="skeleton"
      className={cn("bg-stone-100 animate-pulse rounded-md dark:bg-stone-800", className)}
      {...props}
    />
  )
}

export { Skeleton }
