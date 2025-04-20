"use client"

import { cn } from "@/lib/utils"
import React, { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"

export type BentoGridConstraints = {
  minRows?: number
  maxRows?: number
  minCols?: number
  maxCols?: number
  startRow?: number
  startCol?: number
}

export type BentoGridItem = {
  title: string
  description: string
  header?: React.ReactNode
  className?: string
  content?: React.ReactNode
  constraints?: BentoGridConstraints
  id: string
}

interface BentoGridProps {
  items: BentoGridItem[]
  className?: string
  title?: string
  subtitle?: string
  defaultConstraints?: BentoGridConstraints
  totalCols?: number
  totalRows?: number
}

export function BentoGrid({
  items,
  className,
  title,
  subtitle,
  defaultConstraints = { minRows: 1, maxRows: 1, minCols: 1, maxCols: 1 },
  totalCols = 3,
  totalRows = 2,
}: BentoGridProps) {
  const [active, setActive] = useState<BentoGridItem | null>(null)
  const ref = useRef<HTMLDivElement>(null)

  useOutsideClick(ref as React.RefObject<HTMLDivElement>, () => {
    setActive(null)
  })

  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setActive(null)
      }
    }

    document.addEventListener("keydown", handleEscape)
    return () => document.removeEventListener("keydown", handleEscape)
  }, [])

  return (
    <div className={cn("mx-auto w-full max-w-7xl", className)}>
      {title && (
        <h2 className="text-bold font-sans text-xl font-bold tracking-tight text-neutral-800 dark:text-neutral-100 md:text-4xl">
          {title}
        </h2>
      )}
      {subtitle && (
        <p className="mt-4 max-w-lg text-sm text-neutral-600 dark:text-neutral-400">
          {subtitle}
        </p>
      )}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gridTemplateRows: "auto auto auto auto",
          gap: "0.5rem",
          gridTemplateAreas: `
            "action action action action"
            "steering steering backbone backbone"
            "steering steering backbone backbone"
            "foundation foundation foundation foundation"
          `,
        }}
        className="py-2"
      >
        <AnimatePresence>
          {active && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black/50"
            />
          )}
        </AnimatePresence>
        {active && (
          <div className="fixed inset-0 z-50 grid place-items-center">
            <motion.div
              layoutId={`card-${active.id}`}
              ref={ref}
              className="mx-4 w-full max-w-2xl rounded-2xl bg-white p-6 shadow-xl dark:bg-neutral-900"
            >
              <motion.div layoutId={`header-${active.id}`}>
                {active.header}
              </motion.div>
              <motion.div layoutId={`title-${active.id}`}>
                <CardTitle>{active.title}</CardTitle>
              </motion.div>
              <motion.div layoutId={`description-${active.id}`}>
                <CardDescription>{active.description}</CardDescription>
              </motion.div>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="mt-4"
              >
                {Array.isArray(active.content) ? (
                  <div className="mt-6 rounded-lg bg-neutral-50 p-4 dark:bg-neutral-800">
                    <h4 className="mb-3 font-semibold text-neutral-900 dark:text-neutral-100">
                      What this looks like:
                    </h4>
                    <ul className="list-inside space-y-2">
                      {active.content.map((example, index) => (
                        <li key={index} className="flex items-start">
                          <span className="mr-2 mt-1 text-neutral-500">•</span>
                          <span className="text-sm text-neutral-700 dark:text-neutral-300">
                            {example}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  active.content
                )}
              </motion.div>
            </motion.div>
          </div>
        )}
        {items.map((item) => {
          const areaMap = {
            "Steering Committee": "steering",
            "Action Clusters": "action",
            "Backbone Support Network": "backbone",
            "CoLab Foundation": "foundation",
          }

          const gridArea = areaMap[item.title as keyof typeof areaMap]

          return (
            <motion.div
              layoutId={`card-${item.id}`}
              key={item.id}
              onClick={() => setActive(item)}
              className={cn(
                "group/bento relative min-h-[200px] cursor-pointer overflow-hidden rounded-xl border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-950",
                item.className
              )}
              style={{ gridArea }}
            >
              <div className="absolute inset-0 bg-gradient-to-t from-neutral-100 to-transparent opacity-0 transition-opacity group-hover/bento:opacity-100 dark:from-neutral-900" />
              <div className="p-3">
                <motion.div layoutId={`header-${item.id}`}>
                  {item.header}
                </motion.div>
                <motion.div layoutId={`title-${item.id}`}>
                  <CardTitle>{item.title}</CardTitle>
                </motion.div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

export function Card({
  className,
  children,
  style,
}: {
  className?: string
  children: React.ReactNode
  style?: React.CSSProperties
}) {
  return (
    <motion.div
      whileHover="animate"
      style={style}
      className={cn(
        "group/bento relative overflow-hidden rounded-xl border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-950",
        className
      )}
    >
      <div className="absolute inset-0 bg-gradient-to-t from-neutral-100 to-transparent opacity-0 transition-opacity group-hover/bento:opacity-100 dark:from-neutral-900" />
      {children}
    </motion.div>
  )
}

export function CardContent({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return <div className={cn("p-4", className)}>{children}</div>
}

export function CardTitle({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <h3
      className={cn(
        "font-sans text-lg font-bold tracking-tight text-neutral-800 dark:text-neutral-100",
        className
      )}
    >
      {children}
    </h3>
  )
}

export function CardDescription({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <p
      className={cn(
        "mt-2 text-sm leading-relaxed text-neutral-600 dark:text-neutral-300",
        className
      )}
    >
      {children}
    </p>
  )
}

export const useOutsideClick = (
  ref: React.RefObject<HTMLDivElement>,
  callback: Function
) => {
  useEffect(() => {
    const listener = (event: any) => {
      if (!ref.current || ref.current.contains(event.target)) {
        return
      }
      callback(event)
    }

    document.addEventListener("mousedown", listener)
    document.addEventListener("touchstart", listener)

    return () => {
      document.removeEventListener("mousedown", listener)
      document.removeEventListener("touchstart", listener)
    }
  }, [ref, callback])
}
