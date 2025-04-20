"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { TabIcon } from "./tab-icon"
import React from "react"
import styles from "./stacked-tabs.module.css"

export type StackedTab = {
  title: string
  value: string
  icon?: string
  solutionTitle?: string
  solutionIcon?: string
  content?: React.ReactElement<{
    onToggle?: (isShowingSolution: boolean) => void
    isShowingSolution?: boolean
  }>
}

export interface StackedTabsProps {
  tabs: StackedTab[]
  containerClassName?: string
  activeTabClassName?: string
  tabClassName?: string
  contentClassName?: string
  vertical?: boolean
  showingSolution?: boolean
  onSolutionToggle?: (isShowingSolution: boolean) => void
}

const StackedTabsContent = ({
  className,
  tabs,
  hovering,
  showingSolution,
  onToggle,
  direction,
}: {
  className?: string
  key?: string
  tabs: StackedTab[]
  active: StackedTab
  hovering?: boolean
  showingSolution?: boolean
  onToggle?: (isShowingSolution: boolean) => void
  direction: number
}) => {
  return (
    <div className="relative h-full w-full">
      {tabs.map((tab, idx) => (
        <motion.div
          key={tab.value}
          layoutId={tab.value}
          style={{
            scale: hovering ? 1 - idx * 0.05 : 1,
            left: hovering ? idx * -50 : 0,
            opacity: hovering
              ? idx < 3
                ? 1 - idx * 0.15
                : 0
              : idx === 0
                ? 1
                : 0,
            zIndex: tabs.length - idx,
          }}
          initial={{ x: direction * 40, opacity: 0 }}
          animate={{
            x: 0,
            opacity: idx === 0 ? 1 : 0,
          }}
          exit={{ x: direction * -40, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className={cn(
            "absolute left-0 top-0 h-full w-full bg-background",
            idx === 0 ? "" : "pointer-events-none",
            className
          )}
        >
          {idx === 0 && tab.content && (
            <div className="h-full w-full">
              {React.cloneElement(tab.content, {
                onToggle,
                isShowingSolution: showingSolution,
              })}
            </div>
          )}
        </motion.div>
      ))}
    </div>
  )
}

export function StackedTabs({
  tabs: propTabs,
  containerClassName,
  activeTabClassName,
  tabClassName,
  contentClassName,
  vertical = false,
  showingSolution = false,
  onSolutionToggle,
}: StackedTabsProps) {
  const [active, setActive] = useState<StackedTab>(propTabs[0])
  const [tabs, setTabs] = useState<StackedTab[]>(propTabs)
  const [hovering, setHovering] = useState(false)
  const [hoveringTab, setHoveringTab] = useState<string | null>(null)
  const [direction, setDirection] = useState(0)

  const moveSelectedTabToTop = (idx: number, newDirection: number) => {
    const newTabs = [...propTabs]
    const selectedTab = newTabs.splice(idx, 1)
    newTabs.unshift(selectedTab[0])
    setTabs(newTabs)
    setActive(newTabs[0])
    setDirection(newDirection)
  }

  const handleSolutionToggle = (isShowingSolution: boolean) => {
    onSolutionToggle?.(isShowingSolution)
  }

  const nextTab = () => {
    const currentIndex = propTabs.findIndex((tab) => tab.value === active.value)
    const nextIndex = (currentIndex + 1) % propTabs.length
    moveSelectedTabToTop(nextIndex, 1)
  }

  const prevTab = () => {
    const currentIndex = propTabs.findIndex((tab) => tab.value === active.value)
    const prevIndex =
      currentIndex === 0 ? propTabs.length - 1 : currentIndex - 1
    moveSelectedTabToTop(prevIndex, -1)
  }

  return (
    <div className={cn("relative flex flex-col gap-8")}>
      <div className="relative flex items-center px-2">
        <button
          onClick={prevTab}
          className="absolute -left-4 z-0 flex h-12 w-12 items-center justify-center rounded-r-xl bg-background/90 shadow-lg backdrop-blur-sm hover:bg-background"
        >
          ←
        </button>
        <div
          className={cn(
            "relative z-10 w-full overflow-x-auto px-4",
            styles.noVisibleScrollbar
          )}
        >
          <div
            className={cn(
              "flex min-w-full flex-row items-center justify-center gap-4 py-4",
              styles.noVisibleScrollbar,
              containerClassName
            )}
          >
            {propTabs.map((tab, idx) => {
              const isActive = active.value === tab.value
              const isHovering = hoveringTab === tab.value
              return (
                <motion.div
                  key={tab.title}
                  className="relative flex-shrink-0"
                  initial={false}
                  animate={{
                    scale: isActive ? 1.05 : 1,
                  }}
                  transition={{ duration: 0.2 }}
                >
                  <motion.button
                    onClick={() => {
                      const currentIndex = propTabs.findIndex(
                        (t) => t.value === active.value
                      )
                      moveSelectedTabToTop(idx, idx > currentIndex ? 1 : -1)
                    }}
                    onMouseEnter={() => {
                      setHovering(true)
                      setHoveringTab(tab.value)
                    }}
                    onMouseLeave={() => {
                      setHovering(false)
                      setHoveringTab(null)
                    }}
                    className={cn(
                      "group relative flex flex-col items-center gap-2 rounded-xl p-2 transition-all duration-300 hover:bg-muted/50",
                      isActive && "min-w-[48px]",
                      tabClassName
                    )}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="active-tab"
                        className={cn(
                          "absolute inset-0 rounded-xl bg-gray-200 dark:bg-zinc-800",
                          activeTabClassName
                        )}
                      />
                    )}

                    <div className="relative">
                      {showingSolution
                        ? tab.solutionIcon && (
                            <TabIcon
                              name={tab.solutionIcon}
                              isActive={isActive}
                              size={24}
                            />
                          )
                        : tab.icon && (
                            <TabIcon
                              name={tab.icon}
                              isActive={isActive}
                              size={24}
                            />
                          )}
                    </div>

                    <AnimatePresence>
                      {(isActive || isHovering) && (
                        <motion.span
                          initial={{ opacity: 0, width: 0 }}
                          animate={{ opacity: 1, width: "auto" }}
                          exit={{ opacity: 0, width: 0 }}
                          className="relative whitespace-nowrap text-center text-xs font-medium text-black dark:text-white"
                        >
                          {showingSolution ? tab.solutionTitle : tab.title}
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </motion.button>
                </motion.div>
              )
            })}
          </div>
        </div>
        <button
          onClick={nextTab}
          className="absolute -right-4 z-0 flex h-12 w-12 items-center justify-center rounded-l-xl bg-background/90 shadow-lg backdrop-blur-sm hover:bg-background"
        >
          →
        </button>
      </div>
      <div className="relative">
        <StackedTabsContent
          tabs={tabs}
          active={active}
          key={active.value}
          hovering={hovering}
          showingSolution={showingSolution}
          onToggle={handleSolutionToggle}
          className={cn("mt-0", contentClassName)}
          direction={direction}
        />
      </div>
    </div>
  )
}
