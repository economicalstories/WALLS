import { motion, AnimatePresence } from "framer-motion"
import { useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"

interface MotionTooltipProps {
  content: string
  children: React.ReactNode
  className?: string
}

export function MotionTooltip({
  content,
  children,
  className,
}: MotionTooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [position, setPosition] = useState({ x: 0, y: 0, tooltipWidth: 0 })
  const containerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isVisible && containerRef.current && tooltipRef.current) {
      const rect = containerRef.current.getBoundingClientRect()
      const tooltipRect = tooltipRef.current.getBoundingClientRect()
      setPosition({
        x: rect.left + rect.width / 2 - tooltipRect.width / 2,
        y: rect.top,
        tooltipWidth: tooltipRect.width,
      })
    }
  }, [isVisible])

  return (
    <div
      ref={containerRef}
      className="relative"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            ref={tooltipRef}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
            transition={{ duration: 0.2 }}
            style={{
              position: "fixed",
              left: position.x,
              top: position.y - 40,
              transform: "none",
            }}
            className={cn(
              "z-[9999] whitespace-nowrap rounded-md bg-popover px-3 py-2 text-xs text-popover-foreground shadow-md",
              className
            )}
          >
            <div className="absolute -bottom-1 left-1/2 h-2 w-2 -translate-x-1/2 rotate-45 bg-popover" />
            {content}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
