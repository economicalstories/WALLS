"use client"

import { motion, AnimatePresence } from "framer-motion"
import { useState } from "react"
import { cn } from "@/lib/utils"
import Image from "next/image"
import { MotionTooltip } from "./motion-tooltip"
import {
  IconAlertTriangle,
  IconArrowFork,
  IconBrain,
  IconBulb,
  IconChevronRight,
  IconCircleCheck,
  IconClock,
  IconHeartBroken,
  IconMapPin,
  IconMoodSad,
  IconPuzzle,
  IconRocket,
  IconStars,
  IconTools,
} from "@tabler/icons-react"

// Icons for each point type
const PROBLEM_ICONS = [
  {
    icon: IconAlertTriangle,
    tooltip: "How it starts",
  },
  { icon: IconArrowFork, tooltip: "How it unfolds" },
  { icon: IconHeartBroken, tooltip: "How it ends" },
  { icon: IconBrain, tooltip: "Root Cause: Why traditional approaches fail" },
]

const SOLUTION_ICONS = [
  { icon: IconBulb, tooltip: "Our shared model" },
  { icon: IconTools, tooltip: "The human impact" },
  { icon: IconRocket, tooltip: "The result" },
]

interface SolutionTransformProps {
  items: {
    challenge: {
      title: string
      description: string
      points: string[] // Will always have 4 points
      image: string
    }
    solution: {
      title: string
      description: string
      points: string[] // Will always have 3 points
      image: string
    }
  }[]
  onToggle?: (isShowingSolution: boolean) => void
  isShowingSolution: boolean
}

export function SolutionTransform({
  items,
  onToggle,
  isShowingSolution,
}: SolutionTransformProps) {
  const [activeIndex, setActiveIndex] = useState(0)

  const toggleSolution = () => {
    onToggle?.(!isShowingSolution)
  }

  const nextItem = () => {
    const newIndex = (activeIndex + 1) % items.length
    setActiveIndex(newIndex)
    onToggle?.(false)
  }

  const prevItem = () => {
    const newIndex = activeIndex === 0 ? items.length - 1 : activeIndex - 1
    setActiveIndex(newIndex)
    onToggle?.(false)
  }

  const currentItem = items[activeIndex]

  return (
    <div className="relative w-full">
      <div className="overflow-hidden rounded-2xl border border-border">
        <div className="relative grid min-h-[600px] grid-cols-1 md:grid-cols-2">
          {/* Content Side */}
          <motion.div
            className={cn(
              "relative z-10 flex flex-col justify-center overflow-hidden p-8 transition-colors duration-300",
              isShowingSolution
                ? "bg-[rgba(236,253,245,0.5)] dark:bg-[rgba(6,78,59,0.2)]" // Green: light/dark
                : "bg-[rgba(254,242,242,0.5)] dark:bg-[rgba(127,29,29,0.2)]" // Red: light/dark
            )}
            initial={false}
            animate={{ opacity: 1 }}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={`${activeIndex}-${isShowingSolution}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <motion.div
                  className={cn(
                    "text-2xl font-bold",
                    isShowingSolution
                      ? "text-[rgb(6,95,70)] dark:text-[rgb(34,197,94)]" // Light: dark green, Dark: bright green
                      : "text-[rgb(153,27,27)] dark:text-[rgb(248,113,113)]" // Light: dark red, Dark: bright red
                  )}
                >
                  {isShowingSolution
                    ? currentItem.solution.title
                    : currentItem.challenge.title}
                </motion.div>
                <p className="text-xl font-medium leading-relaxed text-foreground/90">
                  {isShowingSolution
                    ? currentItem.solution.description
                    : currentItem.challenge.description}
                </p>
                <ul className="space-y-4">
                  {(isShowingSolution
                    ? currentItem.solution.points
                    : currentItem.challenge.points
                  ).map((point, index) => {
                    const IconConfig = isShowingSolution
                      ? SOLUTION_ICONS[index]
                      : PROBLEM_ICONS[index]
                    return (
                      <motion.li
                        key={point}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center gap-3 overflow-visible"
                      >
                        <div className="relative w-8">
                          <MotionTooltip content={IconConfig.tooltip}>
                            <motion.div
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              transition={{
                                type: "spring",
                                stiffness: 300,
                                damping: 20,
                                delay: index * 0.1,
                              }}
                              className={cn(
                                "relative flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full",
                                isShowingSolution
                                  ? "bg-primary text-primary-foreground"
                                  : "bg-destructive text-destructive-foreground"
                              )}
                            >
                              <IconConfig.icon size={18} strokeWidth={2.5} />
                            </motion.div>
                          </MotionTooltip>
                        </div>
                        <span className="text-foreground">{point}</span>
                      </motion.li>
                    )
                  })}
                </ul>
              </motion.div>
            </AnimatePresence>

            <motion.button
              onClick={toggleSolution}
              className={cn(
                "mt-8 flex items-center justify-center gap-2 rounded-lg px-6 py-3 text-sm font-medium transition-colors",
                isShowingSolution
                  ? "bg-primary text-primary-foreground hover:bg-primary/90"
                  : "bg-destructive text-destructive-foreground hover:bg-destructive/90"
              )}
            >
              {isShowingSolution ? "View Challenge" : "See Our Solution"}
              <motion.span
                animate={{ rotate: isShowingSolution ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                →
              </motion.span>
            </motion.button>
          </motion.div>

          {/* Image Side */}
          <motion.div className="relative h-full overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.div
                key={`${activeIndex}-${isShowingSolution}`}
                initial={{ opacity: 0, scale: 1.1 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3 }}
                className="absolute inset-0"
              >
                <div className="relative h-full w-full">
                  <Image
                    src={
                      isShowingSolution
                        ? currentItem.solution.image
                        : currentItem.challenge.image
                    }
                    alt={
                      isShowingSolution
                        ? currentItem.solution.title
                        : currentItem.challenge.title
                    }
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 100vw, 50vw"
                    priority
                  />
                  <div
                    className={cn(
                      "absolute inset-0 bg-gradient-to-r transition-opacity duration-300",
                      isShowingSolution
                        ? "from-primary/30 to-transparent opacity-70"
                        : "from-destructive/30 to-transparent opacity-60"
                    )}
                  />
                </div>
              </motion.div>
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
