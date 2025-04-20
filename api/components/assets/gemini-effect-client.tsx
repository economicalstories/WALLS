"use client"
import { useScroll, useTransform } from "framer-motion"
import React from "react"
import { GoogleGeminiEffect } from "../ui/google-gemini-effect"

export const GoogleGeminiEffectDemo = () => {
  const ref = React.useRef<HTMLDivElement>(null)
  const containerRef = React.useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end end"],
    container: containerRef,
  })

  // These values control how much of the path is drawn at any point
  const pathLengthFirst = useTransform(scrollYProgress, [0, 0.8], [0.2, 1])
  const pathLengthSecond = useTransform(scrollYProgress, [0, 0.8], [0.15, 1])
  const pathLengthThird = useTransform(scrollYProgress, [0, 0.8], [0.1, 1])
  const pathLengthFourth = useTransform(scrollYProgress, [0, 0.8], [0.05, 1])
  const pathLengthFifth = useTransform(scrollYProgress, [0, 0.8], [0, 1])

  return (
    <div
      ref={containerRef}
      className="h-screen overflow-y-auto [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
    >
      <div
        ref={ref}
        className="relative -mt-20 h-[150vh] w-full overflow-clip rounded-md bg-black dark:border dark:border-white/[0.1]"
      >
        <GoogleGeminiEffect
          pathLengths={[
            pathLengthFirst,
            pathLengthSecond,
            pathLengthThird,
            pathLengthFourth,
            pathLengthFifth,
          ]}
        />
      </div>
    </div>
  )
}
