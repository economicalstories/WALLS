"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"

interface CardStackProps {
  items: {
    id: string
    content: string
  }[]
}

export function CardStack({ items }: CardStackProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [direction, setDirection] = useState(0)

  useEffect(() => {
    // Fixed duration of 10 seconds (in ms)
    const duration = 10000

    const rotate = () => {
      setDirection(1)
      setCurrentIndex((prevIndex) => (prevIndex + 1) % items.length)
    }

    // Set up the interval with fixed duration
    let timeoutId = setTimeout(rotate, duration)

    // Clean up and reset the interval when the component unmounts
    return () => clearTimeout(timeoutId)
  }, [currentIndex, items.length]) // Reset the timer when currentIndex changes

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0,
      scale: 0.5,
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1,
      scale: 1,
    },
    exit: (direction: number) => ({
      zIndex: 0,
      x: direction < 0 ? 1000 : -1000,
      opacity: 0,
      scale: 0.5,
    }),
  }

  return (
    <div className="relative flex h-full items-center justify-center overflow-hidden">
      <AnimatePresence initial={false} custom={direction} mode="popLayout">
        <motion.div
          key={items[currentIndex].id}
          custom={direction}
          variants={slideVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{
            x: { type: "spring", stiffness: 300, damping: 30 },
            opacity: { duration: 0.2 },
            scale: { duration: 0.2 },
          }}
          className="absolute flex w-full max-w-xl items-center justify-center rounded-xl bg-white px-6 py-6 shadow-lg"
        >
          <p className="text-lg text-gray-700 [text-wrap:balance]">
            {items[currentIndex].content}
          </p>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
