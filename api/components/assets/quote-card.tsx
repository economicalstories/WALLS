"use client"

import { cn } from "@/lib/utils"
import { FaQuoteLeft } from "react-icons/fa"

export const Card = ({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) => {
  return (
    <div
      className={cn(
        "group relative rounded-xl border border-transparent bg-white p-4 shadow-[0_1px_1px_rgba(0,0,0,0.05),0_4px_6px_rgba(34,42,53,0.04),0_24px_68px_rgba(47,48,55,0.05),0_2px_3px_rgba(0,0,0,0.04)] dark:border-[rgba(255,255,255,0.10)] dark:bg-[rgba(40,40,40,0.30)] dark:shadow-[2px_4px_16px_0px_rgba(248,248,248,0.06)_inset]",
        className
      )}
    >
      <FaQuoteLeft className="absolute left-2 top-2 text-neutral-300 opacity-50" />
      {children}
    </div>
  )
}

export const Quote = ({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) => {
  return (
    <h3
      className={cn(
        "relative py-2 text-base font-normal text-black dark:text-white",
        className
      )}
    >
      {children}
    </h3>
  )
}

export const QuoteDescription = ({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) => {
  return (
    <p
      className={cn(
        "max-w-sm text-xs font-normal text-neutral-600 dark:text-neutral-400",
        className
      )}
    >
      {children}
    </p>
  )
}

export function QuoteCard({
  quote,
  perspective,
}: {
  quote: string
  perspective: string
}) {
  return (
    <Card>
      <Quote>{quote}</Quote>
      <div className="mt-4">
        <QuoteDescription className="font-medium">
          {perspective}
        </QuoteDescription>
      </div>
    </Card>
  )
}
