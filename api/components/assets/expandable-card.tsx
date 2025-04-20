"use client"

import Image from "next/image"
import React, { useEffect, useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"

export interface ExpandableCardItem {
  title: string
  description: string
  src: string
  content: React.ReactNode
  icon?: React.ReactNode
}

interface ExpandableCardProps {
  items: ExpandableCardItem[]
  className?: string
  gridClassName?: string
}

export function ExpandableCard({
  items,
  className = "",
  gridClassName = "",
}: ExpandableCardProps) {
  const [active, setActive] = useState<null | ExpandableCardItem>(null)
  const ref = useRef<HTMLDivElement>(null)

  useOutsideClick(ref, () => {
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
    <div className={`relative h-full w-full ${className}`}>
      <div className={`mx-auto ${gridClassName}`}>
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
              layoutId={`card-${active.title}`}
              ref={ref}
              key={active.title}
              className="mx-4 w-full max-w-lg rounded-2xl bg-white shadow-xl dark:bg-neutral-900"
            >
              <motion.div layoutId={`image-${active.title}`}>
                <Image
                  src={active.src}
                  alt={active.title}
                  width={800}
                  height={400}
                  className="h-60 w-full rounded-t-2xl object-cover"
                />
              </motion.div>
              <div className="flex flex-col items-start p-6">
                <motion.h3
                  layoutId={`title-${active.title}`}
                  className="text-xl font-bold text-neutral-800 dark:text-neutral-100"
                >
                  {active.title}
                </motion.h3>
                <motion.p
                  layoutId={`description-${active.title}`}
                  className="mt-2 text-sm text-neutral-500 dark:text-neutral-300"
                >
                  {active.description}
                </motion.p>
                <motion.div
                  layout
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="mt-4 text-neutral-600 dark:text-neutral-400"
                >
                  {active.content}
                </motion.div>
              </div>
            </motion.div>
          </div>
        )}
        {items.map((item) => (
          <motion.div
            layoutId={`card-${item.title}`}
            onClick={() => setActive(item)}
            key={item.title}
            className="cursor-pointer rounded-2xl bg-white shadow-md transition-shadow duration-200 hover:shadow-lg dark:bg-neutral-900"
          >
            <motion.div layoutId={`image-${item.title}`}>
              <Image
                src={item.src}
                alt={item.title}
                width={500}
                height={300}
                className="h-48 w-full rounded-t-2xl object-cover"
              />
            </motion.div>
            <div className="flex flex-col items-start p-6">
              <motion.h3
                layoutId={`title-${item.title}`}
                className="text-lg font-bold text-neutral-800 dark:text-neutral-100"
              >
                {item.title}
              </motion.h3>
              <motion.p
                layoutId={`description-${item.title}`}
                className="mt-2 text-sm text-neutral-500 dark:text-neutral-300"
              >
                {item.description}
              </motion.p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export const useOutsideClick = (
  ref: React.RefObject<HTMLDivElement | null>,
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
