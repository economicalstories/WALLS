"use client"

import React, {
  useEffect,
  useRef,
  useState,
  createContext,
  useContext,
} from "react"
import {
  IconArrowNarrowLeft,
  IconArrowNarrowRight,
  IconX,
} from "@tabler/icons-react"
import { cn } from "@/lib/utils"
import { AnimatePresence, motion } from "framer-motion"
import Image, { ImageProps } from "next/image"
import { useOutsideClick } from "@/hooks/use-outside-click"

interface CarouselProps {
  items: React.ReactElement[]
  initialScroll?: number
}

type Card = {
  src: string
  title: string
  category: string
  content: React.ReactNode
}

export const CarouselContext = createContext<{
  onCardClose: (index: number) => void
  currentIndex: number
}>({
  onCardClose: () => {},
  currentIndex: 0,
})

export const Carousel = ({ items, initialScroll = 0 }: CarouselProps) => {
  const carouselRef = React.useRef<HTMLDivElement>(null)
  const [canScrollLeft, setCanScrollLeft] = React.useState(false)
  const [canScrollRight, setCanScrollRight] = React.useState(true)
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (carouselRef.current) {
      carouselRef.current.scrollLeft = initialScroll
      checkScrollability()
    }
  }, [initialScroll])

  const checkScrollability = () => {
    if (carouselRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = carouselRef.current
      setCanScrollLeft(scrollLeft > 0)
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth)
    }
  }

  const scrollLeft = () => {
    if (carouselRef.current) {
      carouselRef.current.scrollBy({ left: -300, behavior: "smooth" })
    }
  }

  const scrollRight = () => {
    if (carouselRef.current) {
      carouselRef.current.scrollBy({ left: 300, behavior: "smooth" })
    }
  }

  const handleCardClose = (index: number) => {
    if (carouselRef.current) {
      const cardWidth = isMobile() ? 230 : 384 // (md:w-96)
      const gap = isMobile() ? 4 : 8
      const scrollPosition = (cardWidth + gap) * (index + 1)
      carouselRef.current.scrollTo({
        left: scrollPosition,
        behavior: "smooth",
      })
      setCurrentIndex(index)
    }
  }

  const isMobile = () => {
    return window && window.innerWidth < 768
  }

  return (
    <CarouselContext.Provider
      value={{ onCardClose: handleCardClose, currentIndex }}
    >
      <div className="relative w-full">
        <div
          className="flex w-full overflow-x-scroll overscroll-x-auto scroll-smooth py-2 [scrollbar-width:none]"
          ref={carouselRef}
          onScroll={checkScrollability}
        >
          <div className="flex flex-row justify-start gap-8 px-4">
            {items.map((item, index) => (
              <motion.div
                initial={{
                  opacity: 0,
                  y: 20,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                  transition: {
                    duration: 0.5,
                    delay: 0.2 * index,
                    ease: "easeOut",
                    once: true,
                  },
                }}
                key={"card" + index}
                className="w-[280px] md:w-[400px]"
              >
                {item}
              </motion.div>
            ))}
          </div>
        </div>
        <div className="mr-10 mt-2 flex justify-end gap-2">
          <button
            className="relative z-40 flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 disabled:opacity-50"
            onClick={scrollLeft}
            disabled={!canScrollLeft}
          >
            <IconArrowNarrowLeft className="h-6 w-6 text-gray-500" />
          </button>
          <button
            className="relative z-40 flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 disabled:opacity-50"
            onClick={scrollRight}
            disabled={!canScrollRight}
          >
            <IconArrowNarrowRight className="h-6 w-6 text-gray-500" />
          </button>
        </div>
      </div>
    </CarouselContext.Provider>
  )
}

export const Card = ({
  card,
  index,
  layout = false,
}: {
  card: Card
  index: number
  layout?: boolean
}) => {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(
    null
  ) as React.RefObject<HTMLDivElement>
  const { onCardClose, currentIndex } = useContext(CarouselContext)

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        handleClose()
      }
    }

    if (open) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = "auto"
    }

    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [open])

  useOutsideClick(containerRef, () => handleClose())

  const handleOpen = () => {
    setOpen(true)
  }

  const handleClose = () => {
    setOpen(false)
    onCardClose(index)
  }

  return (
    <>
      <AnimatePresence>
        {open && (
          <div className="fixed inset-0 z-[100] flex h-full items-center justify-center overflow-y-auto overflow-x-hidden p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 h-full w-full bg-black/80 backdrop-blur-lg"
            />
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              ref={containerRef}
              layoutId={layout ? `card-${card.title}` : undefined}
              className={cn(
                "relative z-[110] mx-auto my-8 h-fit w-full max-w-5xl rounded-3xl p-4 font-sans shadow-xl md:p-10",
                card.title === "Spark" &&
                  "bg-gradient-to-br from-orange-50 via-white to-orange-50 dark:from-orange-950 dark:via-neutral-900 dark:to-orange-950",
                card.title === "Sculpt" &&
                  "bg-gradient-to-br from-purple-50 via-white to-purple-50 dark:from-purple-950 dark:via-neutral-900 dark:to-purple-950",
                card.title === "Steward" &&
                  "bg-gradient-to-br from-teal-50 via-white to-teal-50 dark:from-teal-950 dark:via-neutral-900 dark:to-teal-950"
              )}
            >
              <motion.div
                className={cn(
                  "absolute inset-0 -z-10 rounded-3xl opacity-20",
                  card.title === "Spark" &&
                    "bg-[radial-gradient(circle_at_50%_120%,rgba(217,119,6,0.4),rgba(0,0,0,0)_70%)]",
                  card.title === "Sculpt" &&
                    "bg-[radial-gradient(circle_at_50%_120%,rgba(147,51,234,0.4),rgba(0,0,0,0)_70%)]",
                  card.title === "Steward" &&
                    "bg-[radial-gradient(circle_at_50%_120%,rgba(15,118,110,0.4),rgba(0,0,0,0)_70%)]"
                )}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 0.2 }}
                transition={{ duration: 0.5 }}
              />
              {card.title === "Spark" && (
                <motion.div
                  className="absolute inset-0 -z-10"
                  initial="hidden"
                  animate="visible"
                >
                  {[...Array(3)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute h-px w-[20%] bg-gradient-to-r from-transparent via-orange-400 to-transparent"
                      style={{
                        left: `${Math.random() * 80}%`,
                        top: `${Math.random() * 100}%`,
                      }}
                      initial={{ scaleX: 0, opacity: 0 }}
                      animate={{
                        scaleX: [0, 1, 0],
                        opacity: [0, 1, 0],
                        transition: {
                          duration: 0.5,
                          delay: i * 0.2 + Math.random() * 2,
                          repeat: Infinity,
                          repeatDelay: Math.random() * 3,
                        },
                      }}
                    />
                  ))}
                </motion.div>
              )}
              {card.title === "Sculpt" && (
                <motion.div
                  className="absolute inset-0 -z-10 overflow-hidden"
                  initial="hidden"
                  animate="visible"
                >
                  {[...Array(5)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute h-16 w-16 rounded-full bg-purple-100 dark:bg-purple-900/30"
                      style={{
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                      }}
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{
                        scale: [0, 1, 0],
                        opacity: [0, 0.3, 0],
                        transition: {
                          duration: 3,
                          delay: i * 0.5,
                          repeat: Infinity,
                          repeatDelay: Math.random() * 2,
                        },
                      }}
                    />
                  ))}
                </motion.div>
              )}
              {card.title === "Steward" && (
                <motion.div
                  className="absolute inset-0 -z-10 overflow-hidden"
                  initial="hidden"
                  animate="visible"
                >
                  {[...Array(8)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute h-8 w-8 rounded-full border border-teal-200 dark:border-teal-800"
                      style={{
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                      }}
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{
                        scale: [0, 1.5],
                        opacity: [0, 0.2, 0],
                        transition: {
                          duration: 4,
                          delay: i * 0.3,
                          repeat: Infinity,
                          repeatDelay: Math.random() * 3,
                        },
                      }}
                    />
                  ))}
                </motion.div>
              )}
              <button
                className={cn(
                  "absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full md:right-6 md:top-6",
                  card.title === "Spark" && "bg-orange-600 hover:bg-orange-700",
                  card.title === "Sculpt" &&
                    "bg-purple-600 hover:bg-purple-700",
                  card.title === "Steward" && "bg-teal-600 hover:bg-teal-700"
                )}
                onClick={handleClose}
              >
                <IconX className="h-6 w-6 text-white" />
              </button>
              <motion.p
                layoutId={layout ? `category-${card.title}` : undefined}
                className={cn(
                  "text-base font-medium",
                  card.title === "Spark" &&
                    "text-orange-700 dark:text-orange-300",
                  card.title === "Sculpt" &&
                    "text-purple-700 dark:text-purple-300",
                  card.title === "Steward" && "text-teal-700 dark:text-teal-300"
                )}
              >
                {card.category}
              </motion.p>
              <motion.p
                layoutId={layout ? `title-${card.title}` : undefined}
                className={cn(
                  "mt-4 text-2xl font-semibold md:text-5xl",
                  card.title === "Spark" &&
                    "text-orange-950 dark:text-orange-50",
                  card.title === "Sculpt" &&
                    "text-purple-950 dark:text-purple-50",
                  card.title === "Steward" && "text-teal-950 dark:text-teal-50"
                )}
              >
                {card.title}
              </motion.p>
              <div className="py-10">{card.content}</div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
      <motion.button
        layoutId={layout ? `card-${card.title}` : undefined}
        onClick={handleOpen}
        className="relative z-10 flex h-[400px] w-full flex-col items-start justify-start overflow-hidden rounded-3xl bg-gray-100 dark:bg-neutral-900 md:h-[500px]"
      >
        <div className="pointer-events-none absolute inset-x-0 top-0 z-30 h-full bg-gradient-to-b from-black/50 via-transparent to-transparent" />
        <div className="relative z-40 p-8">
          <motion.p
            layoutId={layout ? `category-${card.category}` : undefined}
            className="text-left font-sans text-sm font-medium text-white md:text-base"
          >
            {card.category}
          </motion.p>
          <motion.p
            layoutId={layout ? `title-${card.title}` : undefined}
            className="mt-2 max-w-xs text-left font-sans text-xl font-semibold text-white [text-wrap:balance] md:text-3xl"
          >
            {card.title}
          </motion.p>
        </div>
        <BlurImage
          src={card.src}
          alt={card.title}
          fill
          className="absolute inset-0 z-10 object-cover"
        />
      </motion.button>
    </>
  )
}

export const BlurImage = ({
  height,
  width,
  src,
  className,
  alt,
  ...rest
}: ImageProps) => {
  const [isLoading, setLoading] = useState(true)
  return (
    <Image
      className={cn(
        "transition duration-300",
        isLoading ? "blur-sm" : "blur-0",
        className
      )}
      onLoad={() => setLoading(false)}
      src={src}
      width={width}
      height={height}
      loading="lazy"
      decoding="async"
      blurDataURL={typeof src === "string" ? src : undefined}
      alt={alt ? alt : "Background of a beautiful view"}
      {...rest}
    />
  )
}
