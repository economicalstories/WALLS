import { ReactNode } from "react"
import { Spotlight } from "@/components/ui/spotlight"
import { cn } from "@/lib/utils"

interface SpotlightSectionProps {
  title: string | ReactNode
  subtitle: string | ReactNode
  description: string
  children?: ReactNode
  theme: "amber" | "purple" | "emerald"
  className?: string
}

const themeConfig = {
  amber: {
    gradient:
      "from-amber-50/50 to-amber-100/50 dark:from-amber-900/30 dark:to-amber-800/30",
    spotlightFirst:
      "radial-gradient(68.54% 68.72% at 55.02% 31.46%, hsla(45, 100%, 85%, .1) 0, hsla(45, 100%, 55%, .05) 50%, hsla(45, 100%, 45%, 0) 80%)",
    spotlightSecond:
      "radial-gradient(50% 50% at 50% 50%, hsla(45, 100%, 85%, .08) 0, hsla(45, 100%, 55%, .05) 80%, transparent 100%)",
    spotlightThird:
      "radial-gradient(50% 50% at 50% 50%, hsla(45, 100%, 85%, .06) 0, hsla(45, 100%, 45%, .05) 80%, transparent 100%)",
    titleColor: "text-amber-600 dark:text-amber-400",
  },
  purple: {
    gradient:
      "from-purple-50/50 to-purple-100/50 dark:from-purple-900/30 dark:to-purple-800/30",
    spotlightFirst:
      "radial-gradient(68.54% 68.72% at 55.02% 31.46%, hsla(270, 100%, 85%, .1) 0, hsla(270, 100%, 55%, .05) 50%, hsla(270, 100%, 45%, 0) 80%)",
    spotlightSecond:
      "radial-gradient(50% 50% at 50% 50%, hsla(270, 100%, 85%, .08) 0, hsla(270, 100%, 55%, .05) 80%, transparent 100%)",
    spotlightThird:
      "radial-gradient(50% 50% at 50% 50%, hsla(270, 100%, 85%, .06) 0, hsla(270, 100%, 45%, .05) 80%, transparent 100%)",
    titleColor: "text-purple-600 dark:text-purple-400",
  },
  emerald: {
    gradient:
      "from-emerald-50/50 to-emerald-100/50 dark:from-emerald-900/30 dark:to-emerald-800/30",
    spotlightFirst:
      "radial-gradient(68.54% 68.72% at 55.02% 31.46%, hsla(160, 100%, 85%, .1) 0, hsla(160, 100%, 55%, .05) 50%, hsla(160, 100%, 45%, 0) 80%)",
    spotlightSecond:
      "radial-gradient(50% 50% at 50% 50%, hsla(160, 100%, 85%, .08) 0, hsla(160, 100%, 55%, .05) 80%, transparent 100%)",
    spotlightThird:
      "radial-gradient(50% 50% at 50% 50%, hsla(160, 100%, 85%, .06) 0, hsla(160, 100%, 45%, .05) 80%, transparent 100%)",
    titleColor: "text-emerald-600 dark:text-emerald-400",
  },
}

export function SpotlightSection({
  title,
  subtitle,
  description,
  children,
  theme,
  className,
}: SpotlightSectionProps) {
  const config = themeConfig[theme]

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg bg-gradient-to-br",
        config.gradient,
        className
      )}
    >
      <Spotlight
        gradientFirst={config.spotlightFirst}
        gradientSecond={config.spotlightSecond}
        gradientThird={config.spotlightThird}
        translateY={-200}
        width={400}
        height={800}
        smallWidth={200}
        duration={10}
        xOffset={50}
      />
      <div className="relative z-10 p-12">
        <h3
          className={cn(
            "mt-0 text-4xl font-bold",
            typeof title === "string"
              ? "bg-gradient-to-br from-neutral-900 to-neutral-600 bg-clip-text text-transparent dark:from-neutral-100 dark:to-neutral-400"
              : "text-neutral-900 dark:text-neutral-100"
          )}
        >
          {title}
        </h3>
        <p className={cn("mt-4 text-2xl font-semibold", config.titleColor)}>
          {subtitle}
        </p>
        <p className="mt-6 text-xl leading-relaxed text-neutral-700 dark:text-neutral-300">
          {description}
        </p>
        {children && <div className="mt-8">{children}</div>}
      </div>
    </div>
  )
}
