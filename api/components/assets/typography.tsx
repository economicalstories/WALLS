"use client"

import { cn } from "@/lib/utils"
import type { JSX } from "react"

type VariantType =
  | "h1"
  | "h2"
  | "h3"
  | "h4"
  | "p"
  | "blockquote"
  | "code"
  | "lead"
  | "large"
  | "small"
  | "muted"

interface TypographyProps {
  variant?: VariantType
  as?: keyof JSX.IntrinsicElements
  className?: string
  children?: React.ReactNode
  dangerouslySetInnerHTML?: {
    __html: string
  }
}

const variants: Record<VariantType, string> = {
  h1: "scroll-m-20 text-4xl font-extrabold tracking-tight text-foreground lg:text-5xl",
  h2: "scroll-m-20 text-3xl font-semibold tracking-tight text-foreground",
  h3: "scroll-m-20 text-2xl font-semibold tracking-tight text-foreground",
  h4: "scroll-m-20 text-xl font-semibold tracking-tight text-foreground",
  p: "leading-7 text-foreground [&:not(:first-child)]:mt-6",
  blockquote: "mt-6 border-l-2 pl-6 italic text-foreground",
  code: "relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm font-semibold text-foreground",
  lead: "text-xl text-muted-foreground",
  large: "text-lg font-semibold text-foreground",
  small: "text-sm font-medium leading-none text-foreground",
  muted: "text-sm text-muted-foreground",
}

const elements: Record<VariantType, keyof JSX.IntrinsicElements> = {
  h1: "h1",
  h2: "h2",
  h3: "h3",
  h4: "h4",
  p: "div",
  blockquote: "blockquote",
  code: "code",
  lead: "div",
  large: "div",
  small: "small",
  muted: "div",
}

export function Typography({
  variant = "p",
  as,
  className,
  children,
  ...props
}: TypographyProps) {
  const Component = (as ?? elements[variant]) as keyof JSX.IntrinsicElements
  return (
    <Component className={cn(variants[variant], className)} {...props}>
      {children}
    </Component>
  )
}

export type { TypographyProps, VariantType }
