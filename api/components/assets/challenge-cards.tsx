"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"

export interface Challenge {
  title: string
  description: string
  details: string[]
  icon?: React.ReactNode
}

interface ChallengeCardsProps {
  challenges: Challenge[]
  className?: string
}

export function ChallengeCards({ challenges, className }: ChallengeCardsProps) {
  const [activeIndex, setActiveIndex] = useState<number>(0)

  return (
    <div className={cn("w-full", className)}>
      {/* Challenge Navigation */}
      <div className="mb-8 flex space-x-4">
        {challenges.map((challenge, index) => (
          <button
            key={index}
            onClick={() => setActiveIndex(index)}
            className={cn(
              "flex-1 rounded-lg px-4 py-3 text-left transition-all duration-200",
              activeIndex === index
                ? "bg-neutral-900 text-white shadow-lg dark:bg-white dark:text-neutral-900"
                : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200 dark:bg-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-700"
            )}
          >
            <h3 className="text-sm font-medium md:text-base">
              {challenge.title}
            </h3>
          </button>
        ))}
      </div>

      {/* Challenge Content */}
      <div className="relative min-h-[400px] overflow-hidden rounded-2xl bg-neutral-100 dark:bg-neutral-800">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeIndex}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="p-6 md:p-8"
          >
            <div className="mx-auto max-w-3xl">
              <h4 className="mb-6 text-xl font-semibold text-neutral-900 dark:text-white md:text-2xl">
                {challenges[activeIndex].title}
              </h4>
              <p className="mb-8 text-neutral-600 dark:text-neutral-300">
                {challenges[activeIndex].description}
              </p>
              <div className="space-y-4">
                {challenges[activeIndex].details.map((detail, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-3"
                  >
                    <div className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-neutral-400 dark:bg-neutral-500" />
                    <p className="text-neutral-600 dark:text-neutral-300">
                      {detail}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
