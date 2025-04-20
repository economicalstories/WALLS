"use client"

import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { CardStack } from "./card-stack"
import { CanvasRevealEffect } from "./canvas-reveal-effect"

interface Quote {
  id: string
  content: string
}

interface Challenge {
  id: string
  title: string
  description: string
  quotes: Quote[]
  color?: [number, number, number]
}

const Icon = ({ className, ...rest }: any) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth="1.5"
      stroke="currentColor"
      className={className}
      {...rest}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m6-6H6" />
    </svg>
  )
}

const ChallengeCard = ({ challenge }: { challenge: Challenge }) => {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="group/card relative h-[30rem] w-full overflow-hidden rounded-xl border border-black/[0.2] p-4 dark:border-white/[0.2]"
    >
      <Icon className="absolute -left-3 -top-3 h-6 w-6 text-black dark:text-white" />
      <Icon className="absolute -bottom-3 -left-3 h-6 w-6 text-black dark:text-white" />
      <Icon className="absolute -right-3 -top-3 h-6 w-6 text-black dark:text-white" />
      <Icon className="absolute -bottom-3 -right-3 h-6 w-6 text-black dark:text-white" />

      <AnimatePresence mode="wait">
        {hovered ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute inset-0 h-full w-full rounded-lg"
          >
            <CanvasRevealEffect
              colors={challenge.color ? [challenge.color] : undefined}
              containerClassName="bg-gray-900 rounded-lg"
              animationSpeed={3}
            />
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.2 }}
              className="absolute inset-0 flex items-center justify-center p-6"
            >
              <div className="relative z-10 text-center">
                <h3 className="mb-4 text-2xl font-bold text-white">
                  {challenge.title}
                </h3>
                <p className="text-lg text-white/90">{challenge.description}</p>
              </div>
            </motion.div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute inset-0 flex items-center justify-center"
          >
            <div className="h-[32rem] w-full">
              <CardStack items={challenge.quotes} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export function RevealableQuoteCards({
  challenges,
}: {
  challenges: Challenge[]
}) {
  return (
    <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
      {challenges.map((challenge) => (
        <ChallengeCard key={challenge.id} challenge={challenge} />
      ))}
    </div>
  )
}
