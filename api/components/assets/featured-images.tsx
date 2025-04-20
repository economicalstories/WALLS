"use client"

import Image from "next/image"
import React, { useState, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { BsStarFill } from "react-icons/bs"
import { cn } from "@/lib/utils"
import {
  useFloating,
  autoUpdate,
  offset,
  flip,
  shift,
  arrow,
  FloatingPortal,
} from "@floating-ui/react"

export const FeaturedImages = ({
  textClassName,
  className,
  showStars = false,
  containerClassName,
}: {
  textClassName?: string
  className?: string
  showStars?: boolean
  containerClassName?: string
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  const arrowRef = useRef(null)
  const refs = useRef<(HTMLDivElement | null)[]>([])

  const {
    x,
    y,
    strategy,
    refs: floatingRefs,
    middlewareData: { arrow: { x: arrowX, y: arrowY } = {} },
  } = useFloating({
    open: hoveredIndex !== null,
    placement: "top",
    middleware: [offset(12), flip(), shift(), arrow({ element: arrowRef })],
    whileElementsMounted: autoUpdate,
  })

  const handleMouseEnter = (idx: number, element: HTMLDivElement) => {
    floatingRefs.setReference(element)
    setHoveredIndex(idx)
  }

  return (
    <div
      className={cn(
        "mb-10 mt-10 flex flex-col items-center overflow-visible",
        containerClassName
      )}
    >
      <div
        className={cn(
          "mb-2 flex flex-col items-center justify-center overflow-visible sm:flex-row",
          className
        )}
      >
        <div className="mb-4 flex flex-row items-center overflow-visible sm:mb-0">
          {testimonials.map((testimonial, idx) => (
            <div
              ref={(el) => {
                if (el) refs.current[idx] = el
              }}
              className="group relative -mr-6"
              key={testimonial.name}
              onMouseEnter={() =>
                refs.current[idx] && handleMouseEnter(idx, refs.current[idx]!)
              }
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <motion.div
                initial={{
                  opacity: 0,
                }}
                animate={{
                  rotate: `${Math.random() * 15 - 5}deg`,
                  scale: 1,
                  opacity: 1,
                }}
                whileHover={{
                  scale: 1.05,
                  zIndex: 30,
                }}
                transition={{
                  duration: 0.2,
                }}
                className="relative overflow-hidden rounded-2xl border-2 border-white/20 bg-white/10 backdrop-blur-sm"
              >
                <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-white/90 p-2">
                  <Image
                    height={100}
                    width={100}
                    src={testimonial.image}
                    alt={testimonial.name}
                    className={cn(
                      "h-full w-full object-contain",
                      testimonial.name === "Tech Council of Australia" &&
                        "brightness-[1.4] contrast-[1.3] hue-rotate-[180deg] invert-[0.7] saturate-[3]"
                    )}
                  />
                </div>
              </motion.div>
            </div>
          ))}

          <FloatingPortal>
            {hoveredIndex !== null && (
              <AnimatePresence>
                <motion.div
                  ref={floatingRefs.setFloating}
                  initial={{ opacity: 0, y: 10, scale: 0.9 }}
                  animate={{
                    opacity: 1,
                    y: 0,
                    scale: 1,
                    transition: {
                      type: "spring",
                      stiffness: 200,
                      damping: 20,
                    },
                  }}
                  exit={{
                    opacity: 0,
                    y: 10,
                    scale: 0.9,
                    transition: {
                      duration: 0.2,
                    },
                  }}
                  style={{
                    position: strategy,
                    top: y ?? 0,
                    left: x ?? 0,
                    width: "max-content",
                  }}
                  className="z-[9999] flex flex-col items-center justify-center rounded-md bg-neutral-900 px-4 py-2 text-white shadow-xl"
                >
                  <div className="absolute inset-x-0 -bottom-px z-30 mx-auto h-px w-[20%] bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />
                  <div className="absolute inset-x-0 -bottom-px z-30 mx-auto h-px w-[70%] bg-gradient-to-r from-transparent via-sky-500 to-transparent" />
                  <div className="flex items-center gap-2">
                    <div className="relative z-30 text-sm font-bold">
                      {testimonials[hoveredIndex].name}
                    </div>
                    <div className="rounded-sm bg-neutral-950 px-1 py-0.5 text-xs text-neutral-300">
                      {testimonials[hoveredIndex].designation}
                    </div>
                  </div>
                  <div
                    ref={arrowRef}
                    className="absolute -bottom-1 left-1/2 h-2 w-2 -translate-x-1/2 rotate-45 bg-neutral-900"
                    style={{
                      left: arrowX != null ? `${arrowX}px` : "",
                      top: arrowY != null ? `${arrowY}px` : "",
                    }}
                  />
                </motion.div>
              </AnimatePresence>
            )}
          </FloatingPortal>
        </div>

        <div className="ml-6 flex justify-center">
          {[...Array(5)].map((_, index) => (
            <BsStarFill
              key={index}
              className={showStars ? "mx-1 h-4 w-4 text-yellow-400" : "hidden"}
            />
          ))}
        </div>
      </div>
      <p
        className={cn(
          "relative z-40 text-center text-sm text-neutral-400",
          textClassName
        )}
      >
        ...and 50+ signatories from governments, industry, academia, and civil
        society
      </p>
    </div>
  )
}

const testimonials = [
  {
    name: "Australia-New Zealand School of Government",
    designation: "Academic Partner",
    image: "/images/logos/anzsog.jpg",
  },
  {
    name: "IBM",
    designation: "Industry Partner",
    image: "/images/logos/IBM.svg",
  },
  {
    name: "NSW Government",
    designation: "Public Sector",
    image: "/images/logos/NSWGovt.svg",
  },
  {
    name: "Australian Government",
    designation: "Public Sector",
    image: "/images/logos/Australian-Government.svg",
  },
  {
    name: "Gradient Institute",
    designation: "Research Partner",
    image: "/images/logos/GradientInstitute.svg",
  },
  {
    name: "Tech Council of Australia",
    designation: "Industry Body",
    image: "/images/logos/Tech_council.svg",
  },
  {
    name: "InfoXChange",
    designation: "Civil Society",
    image: "/images/logos/InfoXChange.svg",
  },
  {
    name: "Inclusive Design Collective",
    designation: "Civil Society",
    image: "/images/logos/InclusiveDesignCollective.png",
  },
]
