import { cn } from "@/lib/utils"
import { useEffect, useState, useRef } from "react"
import * as ScrollArea from "@radix-ui/react-scroll-area"
import { IconAlignLeft } from "@tabler/icons-react"

interface TableOfContentsItem {
  id: string
  title: string
  level: number
}

// Helper functions
function generateId(text: string, index: number): string {
  return `${text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")}-${index}`
}

function getHeadingLevel(element: HTMLElement): number {
  return parseInt(element.tagName[1])
}

function extractTextContent(element: HTMLElement): string {
  return element.textContent || ""
}

function useTableOfContents() {
  const [items, setItems] = useState<TableOfContentsItem[]>([])
  const processingRef = useRef<boolean>(false)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(
    undefined
  )

  useEffect(() => {
    const processHeadings = () => {
      if (processingRef.current) return
      processingRef.current = true

      const mainContent = document.querySelector("main")
      if (!mainContent) {
        processingRef.current = false
        return
      }

      try {
        // Get all h1 and h2 headings
        const allHeadings = Array.from(mainContent.querySelectorAll("h1, h2"))

        // Filter out headings that are within navigation areas or the table of contents itself
        const contentHeadings = allHeadings.filter((heading) => {
          const isInNavigation = heading.closest('[role="navigation"]') !== null
          const isInTableOfContents =
            heading.closest('[role="complementary"]') !== null
          const isInSidebar = heading.closest(".fixed") !== null
          const isInDimensionCards =
            heading.closest(".dimension-cards") !== null
          const isInTracingBeam = heading.closest(".lg\\:block") !== null

          // Check if heading is in a hidden state
          const isHidden =
            heading.closest('[hidden], [aria-hidden="true"]') !== null

          // Special handling for persona content visibility
          const personaSection = heading.closest(".scroll-area-viewport")
          if (personaSection) {
            // Check if this heading is part of the currently selected persona
            const personaCard = heading.closest(
              "[data-radix-scroll-area-viewport]"
            )
            if (personaCard) {
              // Check if this is the active persona by looking at parent scroll area's data-state
              const scrollArea = personaCard.closest('[role="tabpanel"]')
              const isVisible = scrollArea
                ? scrollArea.getAttribute("data-state") === "active"
                : false
              if (!isVisible) return false
            }
          }

          // Only process visible headings
          if (isHidden) return false

          // Process tab panel headings without modifying DOM
          const tabPanel = heading.closest('[role="tabpanel"]')
          let title = heading.textContent || ""

          if (tabPanel) {
            const tabId = tabPanel.getAttribute("aria-labelledby")
            if (tabId) {
              const tabTrigger = document.getElementById(tabId)
              if (tabTrigger) {
                const tabText = tabTrigger.textContent || ""
                // Check if the heading text already includes the tab text to avoid duplication
                if (!title.includes(tabText)) {
                  title = `${tabText} - ${title}`
                }
              }
            }
          }

          // Special handling for persona dashboard content
          if (personaSection) {
            const personaName = personaSection.querySelector("h2")?.textContent
            if (personaName && !title.includes(personaName)) {
              title = `${personaName} - ${title}`
            }
          }

          heading.setAttribute("data-toc-title", title)

          return (
            !isInNavigation &&
            !isInTableOfContents &&
            !isInSidebar &&
            !isInDimensionCards &&
            !isInTracingBeam &&
            !isHidden
          )
        })

        const processedHeadings = contentHeadings.map((heading, index) => {
          const element = heading as HTMLElement
          const title =
            element.getAttribute("data-toc-title") ||
            extractTextContent(element)
          const existingId = element.id || generateId(title, index)

          if (!element.id) {
            element.id = existingId
          }

          return {
            id: existingId,
            title: title,
            level: getHeadingLevel(element),
          }
        })

        setItems(processedHeadings)
      } finally {
        processingRef.current = false
      }
    }

    // Initial processing
    processHeadings()

    const debouncedProcess = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
      timeoutRef.current = setTimeout(processHeadings, 100)
    }

    const observer = new MutationObserver((mutations) => {
      const hasRelevantChanges = mutations.some((mutation) => {
        // Check for visibility changes in persona sections
        const isPersonaChange =
          mutation.target instanceof Element &&
          (mutation.target.hasAttribute("data-state") ||
            mutation.target.closest("[data-state]") ||
            mutation.target.closest('[role="tabpanel"]'))

        // Check for tab panel changes
        const isTabChange =
          mutation.target instanceof Element &&
          (mutation.target.getAttribute("role") === "tabpanel" ||
            mutation.target.closest('[role="tabpanel"]'))

        // Check for heading changes
        const hasHeadingChanges = Array.from(mutation.addedNodes).some(
          (node) =>
            node instanceof Element &&
            (node.tagName === "H1" || node.tagName === "H2")
        )

        return isPersonaChange || isTabChange || hasHeadingChanges
      })

      if (hasRelevantChanges) {
        debouncedProcess()
      }
    })

    const mainContent = document.querySelector("main")
    if (mainContent) {
      observer.observe(mainContent, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: [
          "hidden",
          "aria-hidden",
          "data-state",
          "style",
          "class",
        ],
      })
    }

    return () => {
      observer.disconnect()
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return items
}

export function TableOfContents() {
  const [mounted, setMounted] = useState(false)
  const [visibleIds, setVisibleIds] = useState<string[]>([])
  const [indicatorStyle, setIndicatorStyle] = useState({ top: 0, height: 0 })
  const itemsRef = useRef<Map<string, HTMLAnchorElement>>(new Map())
  const items = useTableOfContents()

  // Handle mounting state
  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    // Function to check if a section is visible
    const isSectionVisible = (
      start: HTMLElement,
      end: HTMLElement | null,
      isLastSection: boolean
    ) => {
      const startRect = start.getBoundingClientRect()
      const viewportHeight = window.innerHeight

      // Special handling for the last section
      if (isLastSection) {
        // Get the main content container
        const mainContent = start.closest("main")
        if (mainContent) {
          const mainRect = mainContent.getBoundingClientRect()
          // Check if any part of the content from this heading to the bottom is visible
          return (
            (startRect.top < viewportHeight && startRect.bottom >= 0) || // Heading is visible
            (startRect.top <= 0 && mainRect.bottom >= 0) || // Content after heading is visible
            (mainRect.bottom >= 0 && mainRect.bottom <= viewportHeight) // Bottom of content is visible
          )
        }
      }

      // If there's no end element and it's not the last section, use default check
      if (!end) {
        return startRect.top < viewportHeight && startRect.bottom >= 0
      }

      const endRect = end.getBoundingClientRect()

      // Check if any part of the section between start and end is visible
      return (
        (startRect.top < viewportHeight && startRect.bottom >= 0) || // Start element is visible
        (endRect.top < viewportHeight && endRect.bottom >= 0) || // End element is visible
        (startRect.top <= 0 && endRect.bottom >= viewportHeight) // Section spans viewport
      )
    }

    const updateVisibleSections = () => {
      // Get all headings in document order
      const headings = items
        .map((item) => document.getElementById(item.id))
        .filter((el): el is HTMLElement => el !== null)
        .sort(
          (a, b) =>
            a.getBoundingClientRect().top - b.getBoundingClientRect().top
        )

      const newVisibleIds = new Set<string>()

      headings.forEach((heading, index) => {
        const nextHeading = headings[index + 1] || null
        const isLastSection = index === headings.length - 1
        if (isSectionVisible(heading, nextHeading, isLastSection)) {
          newVisibleIds.add(heading.id)
        }
      })

      setVisibleIds(Array.from(newVisibleIds))
    }

    // Create intersection observer for initial detection
    const observer = new IntersectionObserver(updateVisibleSections, {
      rootMargin: "-20% 0px -20% 0px",
      threshold: [0, 0.2, 0.4, 0.6, 0.8, 1],
    })

    // Observe all headings and the main content container
    items.forEach((item) => {
      const element = document.getElementById(item.id)
      if (element) {
        observer.observe(element)
        // For the last heading, also observe its parent container
        if (item === items[items.length - 1]) {
          const mainContent = element.closest("main")
          if (mainContent) {
            observer.observe(mainContent)
          }
        }
      }
    })

    // Add scroll listener for continuous updates
    window.addEventListener("scroll", updateVisibleSections, { passive: true })

    return () => {
      observer.disconnect()
      window.removeEventListener("scroll", updateVisibleSections)
    }
  }, [items, mounted])

  // Update indicator to cover all visible sections
  useEffect(() => {
    if (!mounted || visibleIds.length === 0) return

    // Get all visible items in the table of contents
    const visibleItems = Array.from(itemsRef.current.entries())
      .filter(([id]) => visibleIds.includes(id))
      .map(([_, el]) => el)

    if (visibleItems.length > 0) {
      // Find the top-most and bottom-most visible items
      const firstItem = visibleItems[0]
      const lastItem = visibleItems[visibleItems.length - 1]

      // Calculate the total height to cover all visible sections
      const top = firstItem.offsetTop
      const bottom = lastItem.offsetTop + lastItem.offsetHeight

      setIndicatorStyle({
        top,
        height: bottom - top,
      })
    }
  }, [visibleIds, mounted])

  if (items.length === 0) {
    return null
  }

  return (
    <div className="flex h-full w-[240px] max-w-full flex-col gap-3 pe-2">
      <h3 className="-ms-0.5 inline-flex items-center gap-1.5 text-sm text-muted-foreground">
        <IconAlignLeft className="size-4" />
        On this page
      </h3>
      <ScrollArea.Root className="overflow-hidden">
        <ScrollArea.Viewport
          className="relative size-full min-h-0 rounded-[inherit] text-sm"
          style={{ overflow: "hidden scroll" }}
        >
          <div style={{ minWidth: "100%", display: "table" }}>
            <div className="relative flex flex-col">
              <div className="absolute inset-y-0 start-0 w-px bg-foreground/10" />
              {mounted && visibleIds.length > 0 && (
                <div
                  role="none"
                  className="absolute start-0 z-10 w-px bg-primary transition-all duration-300"
                  style={{
                    top: indicatorStyle.top,
                    height: indicatorStyle.height,
                  }}
                />
              )}
              {items.map((item) => (
                <a
                  key={item.id}
                  ref={(el) => {
                    if (el) {
                      itemsRef.current.set(item.id, el)
                    }
                  }}
                  href={`#${item.id}`}
                  data-active={visibleIds.includes(item.id)}
                  className={cn(
                    "relative py-1.5 text-sm text-muted-foreground transition-colors [overflow-wrap:anywhere] first:pt-0 last:pb-0 hover:text-foreground data-[active=true]:text-primary",
                    item.level === 1 ? "ps-3.5" : "ps-6"
                  )}
                  onClick={(e) => {
                    e.preventDefault()
                    const element = document.getElementById(item.id)
                    if (element) {
                      const yOffset = -100 // Adjust this value based on your header height
                      const y =
                        element.getBoundingClientRect().top +
                        window.pageYOffset +
                        yOffset
                      window.scrollTo({ top: y, behavior: "smooth" })
                    }
                  }}
                >
                  {item.title}
                </a>
              ))}
            </div>
          </div>
        </ScrollArea.Viewport>
      </ScrollArea.Root>
    </div>
  )
}
