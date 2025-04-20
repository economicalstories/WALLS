import { motion, AnimatePresence } from "framer-motion"
import { FiArrowRight } from "react-icons/fi"
import { IconX } from "@tabler/icons-react"
import { cn } from "@/lib/utils"
import { useState } from "react"
import { Zap, Hammer, Sprout } from "lucide-react"
import { Dialog, DialogContent } from "@/components/ui/dialog"

interface DimensionItem {
  title: string
  category: string
  content: React.ReactNode
  src: string
}

interface DimensionCardsProps {
  items: DimensionItem[]
}

const DimensionContent = ({
  title,
  description,
  Icon,
  color,
  whyThisMatters,
  objectives,
}: {
  title: string
  description: string
  Icon: any
  color: string
  whyThisMatters: string[]
  objectives: string[]
}) => {
  return (
    <div className="mb-4 space-y-8 rounded-3xl bg-[#F5F5F7] p-8 dark:bg-neutral-800 md:p-14">
      <div className="flex items-center gap-4">
        <div className="rounded-full p-4" style={{ backgroundColor: color }}>
          <Icon className="h-8 w-8 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-neutral-800 dark:text-neutral-200 md:text-3xl">
          {title}
        </h3>
      </div>

      <p className="max-w-3xl font-sans text-base text-neutral-600 dark:text-neutral-400 md:text-2xl">
        {description}
      </p>

      <div className="space-y-6">
        <div>
          <h4 className="mb-3 text-lg font-semibold text-neutral-800 dark:text-neutral-300">
            Why This Matters
          </h4>
          <ul className="space-y-2">
            {whyThisMatters.map((point, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-neutral-600 dark:text-neutral-400"
              >
                <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-neutral-400" />
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="mb-3 text-lg font-semibold text-neutral-800 dark:text-neutral-300">
            What This Looks Like
          </h4>
          <ul className="space-y-2">
            {objectives.map((objective, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-neutral-600 dark:text-neutral-400"
              >
                <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-neutral-400" />
                <span>{objective}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

export function DimensionCards({ items }: DimensionCardsProps) {
  const [selectedCard, setSelectedCard] = useState<DimensionItem | null>(null)

  return (
    <div className="p-4 md:p-8">
      <div className="dimension-cards grid w-full grid-cols-1 gap-4 md:gap-8 lg:grid-cols-3">
        {items.map((item, index) => (
          <DimensionCard key={index} card={item} index={index} />
        ))}
      </div>
    </div>
  )
}

const DimensionCard = ({
  card,
  index,
}: {
  card: DimensionItem
  index: number
}) => {
  const [isOpen, setIsOpen] = useState(false)

  const handleOpen = () => setIsOpen(true)
  const handleClose = () => setIsOpen(false)

  const getIconAndColor = (title: string) => {
    switch (title) {
      case "Spark":
        return { Icon: Zap, color: "rgb(217, 119, 6)" }
      case "Sculpt":
        return { Icon: Hammer, color: "rgb(147, 51, 234)" }
      case "Steward":
        return { Icon: Sprout, color: "rgb(15, 118, 110)" }
      default:
        return { Icon: Zap, color: "rgb(217, 119, 6)" }
    }
  }

  const { Icon, color } = getIconAndColor(card.title)

  const modalContent = {
    Spark: {
      title: "Capacity and Community",
      description:
        "Building awareness, motivation, and knowledge to enable effective collaboration and AI adoption. We focus on creating new ways of working that allow us to experiment safely and innovate together.",
      whyThisMatters: [
        "When communities understand AI's potential and how to use it, they can drive innovation that serves their needs",
        "A lack of awareness, motivation, and knowledge slows collaboration and AI adoption, limiting our ability to tackle social challenges",
        "New ways of working are needed to experiment safely and innovate together—and these take new skillsets and mindsets",
      ],
      objectives: [
        "Bringing people together across sectors to learn, building confidence with new technologies and approaches that create real impact",
        "Creating hands-on learning experiences where tech partners help everyone get comfortable experimenting with AI",
        "Building a community of pioneers who work together to create solutions and inspire others by showing what's possible",
      ],
    },
    Sculpt: {
      title: "Tools and Techniques",
      description:
        "AI must be actively shaped to address pressing social challenges at scale. This means developing solutions that tackle fundamental human needs - from healthcare access to tackling disadvantage to economic opportunity.",
      whyThisMatters: [
        "Connecting community insights, public sector impact channels, and tech expertise unlocks powerful opportunities for impact",
        "When we rally around real community needs, we attract diverse partners and resources to create lasting solutions",
        "Magic happens when we bring together community wisdom, public sector reach, and technical know-how",
      ],
      objectives: [
        "Collaborative development projects with cross-sector partners to address community needs and challenges",
        "Rally allies around public impact missions to attract and marshal resources, align efforts, and empower communities to drive priorities",
        "Tech experts and domain experts collaborating to build specialised AI solutions that scale",
      ],
    },
    Steward: {
      title: "Assurance and Inclusion",
      description:
        "Creating trusted frameworks and standards that enable responsible innovation and inclusive adoption of AI across sectors.",
      whyThisMatters: [
        "Without proactive stewardship, even well-intentioned AI development risks creating unintended consequences",
        "Inclusive design is essential to ensure AI systems serve everyone, not just the tech-savvy",
        "Safeguards must be inclusive and practical too for the technology to be accessible",
      ],
      objectives: [
        "Creating trusted approaches and standards that enable responsible innovation and inclusive adoption of AI across sectors",
        "Accelerate responsible practices and inclusive adoption across the public, social, and private sector",
        "Share and support socially valuable tools to amplify impact, encourage adoption, and inspire others",
      ],
    },
  }

  const content = modalContent[card.title as keyof typeof modalContent]

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto py-16">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={handleClose}
              className="fixed inset-0 bg-black/60"
            />
            <motion.div
              initial={{ opacity: 0, y: 100, scale: 0.8 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 100, scale: 0.8 }}
              className="relative z-50 mx-4 w-full max-w-4xl overflow-hidden rounded-2xl bg-white p-6 shadow-xl dark:bg-neutral-900 md:p-8"
            >
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
              <DimensionContent
                title={content.title}
                description={content.description}
                Icon={Icon}
                color={color}
                whyThisMatters={content.whyThisMatters}
                objectives={content.objectives}
              />
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <motion.div
        transition={{
          staggerChildren: 0.035,
        }}
        whileHover="hover"
        className="group relative aspect-[1/1.618] w-full cursor-pointer overflow-hidden rounded-3xl bg-slate-300"
        onClick={handleOpen}
      >
        <div
          className="absolute inset-0 saturate-100 transition-all duration-500 group-hover:scale-110 md:saturate-0 md:group-hover:saturate-100"
          style={{
            backgroundImage: `url(${card.src})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
        <div className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-black/90 via-black/60 to-transparent" />
        <div className="relative z-20 flex h-full flex-col justify-between p-8 text-white transition-colors duration-500">
          <FiArrowRight className="ml-auto text-3xl transition-transform duration-500 group-hover:-rotate-45" />
          <div>
            <h4>
              {card.title.split("").map((l, i) => (
                <ShiftLetter letter={l} key={i} />
              ))}
            </h4>
            <p className="mt-2 text-sm md:text-base">{card.category}</p>
          </div>
        </div>
      </motion.div>
    </>
  )
}

const ShiftLetter = ({ letter }: { letter: string }) => {
  return (
    <div className="inline-block h-[36px] overflow-hidden text-3xl font-semibold">
      <motion.span
        className="flex min-w-[4px] flex-col"
        style={{
          y: "0%",
        }}
        variants={{
          hover: {
            y: "-50%",
          },
        }}
        transition={{
          duration: 0.5,
        }}
      >
        <span>{letter}</span>
        <span>{letter}</span>
      </motion.span>
    </div>
  )
}

export default DimensionCards
