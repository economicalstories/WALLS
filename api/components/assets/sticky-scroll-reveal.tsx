"use client"

import React, { useRef, useState } from "react"
import {
  motion,
  useScroll,
  useTransform,
  useMotionValueEvent,
} from "framer-motion"

export interface ScrollRevealItem {
  title: string
  description: string | React.ReactNode
  content?: React.ReactNode
  icon?: React.ReactNode
}

interface StickyScrollRevealProps {
  items: ScrollRevealItem[]
  className?: string
  backgroundColors?: string[]
  headerTitle?: string
  headerDescription?: string | React.ReactNode
}

export function StickyScrollReveal({
  items,
  className = "",
  backgroundColors = ["#1f2937", "#262626", "#1e293b"],
  headerTitle,
  headerDescription,
}: StickyScrollRevealProps) {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  })

  const [gradient, setGradient] = useState(backgroundColors[0])

  useMotionValueEvent(scrollYProgress, "change", (latest) => {
    const itemsBreakpoints = items.map((_, index) => index / items.length)
    const closestBreakpointIndex = itemsBreakpoints.reduce(
      (acc, breakpoint, index) => {
        const distance = Math.abs(latest - breakpoint)
        if (distance < Math.abs(latest - itemsBreakpoints[acc])) {
          return index
        }
        return acc
      },
      0
    )
    setGradient(
      backgroundColors[closestBreakpointIndex % backgroundColors.length]
    )
  })

  return (
    <motion.div
      animate={{
        background: gradient,
      }}
      transition={{
        duration: 0.5,
      }}
      ref={ref}
      className={`sticky-scroll-reveal relative w-full px-4 pt-12 sm:px-6 sm:pt-16 md:pt-24 lg:pt-32 ${className}`}
    >
      {(headerTitle || headerDescription) && (
        <div className="flex flex-col items-center px-4 text-center sm:px-6">
          {headerTitle && (
            <h2 className="text-xl font-bold text-white sm:text-2xl md:text-3xl lg:text-4xl">
              {headerTitle}
            </h2>
          )}
          {headerDescription &&
            (typeof headerDescription === "string" ? (
              <p className="mx-auto mt-3 max-w-2xl text-sm text-white/80 sm:mt-4 sm:text-base md:text-lg">
                {headerDescription}
              </p>
            ) : (
              <div className="mx-auto mt-3 max-w-2xl text-sm text-white/80 sm:mt-4 sm:text-base md:text-lg">
                {headerDescription}
              </div>
            ))}
        </div>
      )}
      <StickyScroll content={items} />
    </motion.div>
  )
}

const StickyScroll = ({ content }: { content: ScrollRevealItem[] }) => {
  return (
    <div className="py-8 sm:py-12 md:py-16 lg:py-20">
      <motion.div className="relative hidden w-full justify-between p-4 sm:p-6 lg:flex lg:h-full lg:flex-col lg:p-8">
        {content.map((item, index) => (
          <ScrollContent key={item.title + index} item={item} index={index} />
        ))}
      </motion.div>
      <motion.div className="relative flex w-full flex-col justify-between p-4 sm:p-6 lg:hidden">
        {content.map((item, index) => (
          <ScrollContentMobile
            key={item.title + index}
            item={item}
            index={index}
          />
        ))}
      </motion.div>
    </div>
  )
}

const ScrollContent = ({
  item,
  index,
}: {
  item: ScrollRevealItem
  index: number
}) => {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  })
  const translate = useTransform(scrollYProgress, [0, 1], [0, 200])
  const translateContent = useTransform(scrollYProgress, [0, 1], [0, 100])
  const opacity = useTransform(
    scrollYProgress,
    [0, 0.05, 0.5, 0.7, 1],
    [0, 1, 1, 0, 0]
  )
  const opacityContent = useTransform(
    scrollYProgress,
    [0, 0.2, 0.5, 0.8, 1],
    [0, 0, 1, 1, 0]
  )

  return (
    <motion.div
      ref={ref}
      transition={{
        duration: 0.3,
      }}
      className="relative my-24 grid grid-cols-1 gap-6 lg:my-32 lg:grid-cols-2 lg:gap-8"
    >
      <div className="w-full px-0 sm:px-4">
        <motion.div
          style={{
            y: translate,
            opacity: index === 0 ? opacityContent : 1,
          }}
        >
          {item.icon && <div className="mb-3">{item.icon}</div>}
          <motion.div className="inline-block bg-gradient-to-b from-white to-white bg-clip-text text-xl font-bold text-transparent sm:text-2xl lg:text-3xl xl:text-4xl">
            {item.title}
          </motion.div>
          <motion.div className="mt-3 max-w-sm text-base text-neutral-300 sm:text-lg">
            {item.description}
          </motion.div>
        </motion.div>
      </div>
      {item.content && (
        <motion.div
          style={{
            y: translateContent,
            opacity: opacity,
          }}
          className="h-full w-full self-start rounded-md"
        >
          {item.content}
        </motion.div>
      )}
    </motion.div>
  )
}

const ScrollContentMobile = ({
  item,
  index,
}: {
  item: ScrollRevealItem
  index: number
}) => {
  return (
    <motion.div
      transition={{
        duration: 0.3,
      }}
      className="relative mb-12 flex flex-col gap-6 px-0 sm:mb-16 sm:px-4 md:flex-row md:gap-8"
    >
      {item.content && (
        <motion.div className="mb-6 w-full self-start rounded-md sm:mb-8">
          {item.content}
        </motion.div>
      )}
      <div className="w-full">
        <motion.div>
          {item.icon && <div className="mb-3">{item.icon}</div>}
          <motion.div className="inline-block bg-gradient-to-b from-white to-white bg-clip-text text-xl font-bold text-transparent sm:text-2xl">
            {item.title}
          </motion.div>
          <motion.div className="mt-3 max-w-sm text-sm text-neutral-300 sm:text-base">
            {item.description}
          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  )
}
