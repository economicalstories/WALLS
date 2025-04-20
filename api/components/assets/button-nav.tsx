import { cn } from "@/lib/utils"
import React from "react"

export const Button: React.FC<{
  children?: React.ReactNode
  className?: string
  variant?: "simple" | "simpledestructive" | "outline" | "primary" | "muted"
  as?: React.ElementType
  [x: string]: any
}> = ({
  children,
  className,
  variant = "primary",
  as: Tag = "button",
  ...props
}) => {
  const variantClass =
    variant === "simple"
      ? "bg-secondary relative z-10 bg-transparent hover:border-secondary hover:bg-secondary/50 border border-transparent text-white text-sm md:text-sm transition font-medium duration-200 rounded-md px-4 py-2 flex items-center justify-center"
      : variant === "simpledestructive"
        ? "bg-destructive relative z-10 bg-transparent hover:border-destructive hover:bg-destructive/50 border border-transparent text-white hover:text-white text-sm md:text-sm transition font-medium duration-200 rounded-md px-4 py-2 flex items-center justify-center"
        : variant === "outline"
          ? "bg-white relative z-10 hover:bg-secondary/90 hover:shadow-xl text-black border border-black hover:text-black text-sm md:text-sm transition font-medium duration-200 rounded-md px-4 py-2 flex items-center justify-center"
          : variant === "primary"
            ? "bg-secondary relative z-10 hover:bg-secondary/90 border border-secondary text-black text-sm md:text-sm transition font-medium duration-200 rounded-md px-4 py-2 flex items-center justify-center shadow-[0px_-1px_0px_0px_#FFFFFF60_inset,_0px_1px_0px_0px_#FFFFFF60_inset]"
            : variant === "muted"
              ? "bg-neutral-800 relative z-10 hover:bg-neutral-900 border border-transparent text-white text-sm md:text-sm transition font-medium duration-200 rounded-md px-4 py-2 flex items-center justify-center shadow-[0px_1px_0px_0px_#FFFFFF20_inset]"
              : ""
  return (
    <Tag
      className={cn(
        "group relative z-10 flex items-center justify-center rounded-md bg-secondary px-4 py-2 text-sm font-medium text-black transition duration-200 hover:-translate-y-0.5 hover:bg-secondary/90 active:scale-[0.98] md:text-sm",
        variantClass,
        className
      )}
      {...props}
    >
      {children ?? `Get Started`}
    </Tag>
  )
}
