"use client"

import { motion } from "framer-motion"
import { IconChevronRight } from "@tabler/icons-react"

interface StrategyFlowProps {
  className?: string
}

export const StrategyFlow = ({ className }: StrategyFlowProps) => {
  const arrowVariants = {
    initial: { x: -10, opacity: 0 },
    animate: {
      x: 0,
      opacity: 1,
      transition: {
        repeat: Infinity,
        duration: 1.5,
        ease: "easeInOut",
      },
    },
  }

  return (
    <div
      className={`flex items-center justify-center gap-2 text-sm text-muted-foreground ${className}`}
    >
      <span>Core Approaches</span>
      <motion.div variants={arrowVariants} initial="initial" animate="animate">
        <IconChevronRight size={20} />
      </motion.div>
      <span>Platform for Collaboration</span>
      <motion.div variants={arrowVariants} initial="initial" animate="animate">
        <IconChevronRight size={20} />
      </motion.div>
      <span>Strategic Outcomes</span>
    </div>
  )
}
