import { useState } from "react"
import Link from "next/link"
import participationActivities from "@/data/participation-activities.json"
import { cn } from "@/lib/utils"
import { IconFlame, IconTools, IconCompass } from "@tabler/icons-react"

interface PersonaLevel {
  motivation: "high" | "low"
  capability: "high" | "low"
  opportunity: "high" | "low"
}

type ActionLevel = "starting_out" | "ready_to_collaborate" | "ready_to_lead"
type ActionSet = "spark" | "sculpt" | "steward"

interface ActivityRequirements {
  motivation: string[]
  capability: string[]
  opportunity: string[]
}

// Questions to determine persona with weighted scoring
const questions = [
  {
    dimension: "motivation",
    primary: {
      text: "How interested are you in engaging with AI and its potential?",
      options: [
        { text: "Not particularly interested at this time", score: 1 },
        { text: "Curious but haven't explored much", score: 2 },
        { text: "Keen to learn and get involved", score: 3 },
        { text: "Passionate about shaping AI's future", score: 4 },
      ],
    },
    secondary: {
      text: "How actively do you want to participate in AI development?",
      options: [
        { text: "Prefer to observe how things develop", score: 1 },
        { text: "Happy to provide input when asked", score: 2 },
        { text: "Want to actively contribute to projects", score: 3 },
        { text: "Want to help drive positive change", score: 4 },
      ],
    },
    weights: { primary: 0.7, secondary: 0.3 },
  },
  {
    dimension: "capability",
    primary: {
      text: "How would you describe your current AI knowledge and experience?",
      options: [
        { text: "I'm new to AI and learning basics", score: 1 },
        { text: "I understand key concepts", score: 2 },
        { text: "I have hands-on experience", score: 3 },
        { text: "I work with AI professionally", score: 4 },
      ],
    },
    secondary: {
      text: "How comfortable are you with applying AI in your domain?",
      options: [
        { text: "Not comfortable yet", score: 1 },
        { text: "Comfortable with guidance", score: 2 },
        { text: "Confident in most situations", score: 3 },
        { text: "Can lead others effectively", score: 4 },
      ],
    },
    weights: { primary: 0.6, secondary: 0.4 },
  },
  {
    dimension: "opportunity",
    primary: {
      text: "What best describes your position to influence AI adoption?",
      options: [
        { text: "Limited influence on decisions", score: 1 },
        { text: "Can suggest and advocate", score: 2 },
        { text: "Manage relevant resources", score: 3 },
        { text: "Direct authority over initiatives", score: 4 },
      ],
    },
    secondary: {
      text: "How ready is your environment for AI innovation?",
      options: [
        { text: "Limited infrastructure or support", score: 1 },
        { text: "Basic resources available", score: 2 },
        { text: "Supportive environment", score: 3 },
        { text: "Strong innovation culture", score: 4 },
      ],
    },
    weights: { primary: 0.7, secondary: 0.3 },
  },
]

interface PersonaRecommendation {
  title: string
  description: string
  focus: string
  actionLevels: Record<ActionSet, ActionLevel>
}

const actionLevelLabels: Record<ActionLevel, string> = {
  starting_out: "Starting\nOut",
  ready_to_collaborate: "Ready to\nCollaborate",
  ready_to_lead: "Ready to\nLead",
}

const actionSetDescriptions: Record<ActionSet, string> = {
  spark: "Building awareness and exploring possibilities",
  sculpt: "Shaping solutions and practices",
  steward: "Guiding responsible implementation",
}

const actionSetContent: Record<ActionSet, Record<ActionLevel, string[]>> = {
  spark: {
    starting_out: [
      "Join hands-on learning experiences",
      "Join community discussions and meet allies",
      "Learn from successful projects",
    ],
    ready_to_collaborate: [
      "Join active Action Clusters",
      "Help others learn from your experiences and perspectives",
      "Champion opportunities and inspire others to get involved",
    ],
    ready_to_lead: [
      "Launch and grow Action Clusters in new domains",
      "Create spaces that bring diverse perspectives together",
      "Build momentum through shared learning and storytelling",
    ],
  },
  sculpt: {
    starting_out: [
      "Explore available building blocks",
      "Test solutions in safe environments",
      "Learn from experts and proven patterns",
    ],
    ready_to_collaborate: [
      "Contribute to joint solutions",
      "Test and use reusable components",
      "Share and adapt proven solutions",
    ],
    ready_to_lead: [
      "Lead solution development",
      "Create shared infrastructure and components",
      "Rally allies around high-impact missions",
    ],
  },
  steward: {
    starting_out: [
      "Learn ethical and responsible practices",
      "Understand inclusion principles",
      "Explore opportunities and challenges of AI for your community",
    ],
    ready_to_collaborate: [
      "Apply ethical and responsible practices",
      "Refine best practices through real-world testing",
      "Seek feedback and validation from experts and communities",
    ],
    ready_to_lead: [
      "Shape best practices that help allies adopt robust systems with confidence",
      "Share practical toolkits and step-by-step guides",
      "Open new domains for safe innovation",
    ],
  },
}

// Persona descriptions and focus areas
const personaRecommendations: Record<string, PersonaRecommendation> = {
  "low-low-low": {
    title: "Skeptical Spectators",
    description:
      "You're thoughtfully cautious about AI's implications and looking to understand more before getting deeply involved.",
    focus: "Building awareness and understanding through trusted channels",
    actionLevels: {
      spark: "starting_out",
      sculpt: "starting_out",
      steward: "starting_out",
    },
  },
  "high-low-low": {
    title: "Eager Explorers",
    description:
      "You're excited about AI's potential and ready to learn more about how to engage effectively.",
    focus: "Building practical knowledge and connections",
    actionLevels: {
      spark: "ready_to_collaborate",
      sculpt: "starting_out",
      steward: "starting_out",
    },
  },
  "low-high-low": {
    title: "Latent Luminaries",
    description:
      "You have valuable technical expertise but are seeking meaningful ways to apply it.",
    focus: "Finding impactful opportunities to apply your skills",
    actionLevels: {
      spark: "starting_out",
      sculpt: "ready_to_collaborate",
      steward: "starting_out",
    },
  },
  "high-high-low": {
    title: "Capable Catalysts",
    description:
      "You combine technical skills with enthusiasm but need more connections to create impact.",
    focus: "Building bridges and finding collaboration opportunities",
    actionLevels: {
      spark: "ready_to_collaborate",
      sculpt: "ready_to_collaborate",
      steward: "ready_to_collaborate",
    },
  },
  "low-low-high": {
    title: "Watchful Wardens",
    description:
      "You have influence over AI adoption but want to ensure responsible implementation.",
    focus: "Ensuring responsible and inclusive AI adoption",
    actionLevels: {
      spark: "starting_out",
      sculpt: "starting_out",
      steward: "ready_to_collaborate",
    },
  },
  "high-low-high": {
    title: "Aspiring Accelerators",
    description:
      "You're eager to drive AI adoption and have the influence to make it happen.",
    focus: "Building capability while maintaining momentum",
    actionLevels: {
      spark: "ready_to_collaborate",
      sculpt: "starting_out",
      steward: "ready_to_collaborate",
    },
  },
  "low-high-high": {
    title: "Dormant Dynamos",
    description:
      "You combine technical expertise with influence but seek alignment with broader impact.",
    focus: "Aligning technical capability with meaningful impact",
    actionLevels: {
      spark: "starting_out",
      sculpt: "ready_to_collaborate",
      steward: "ready_to_collaborate",
    },
  },
  "high-high-high": {
    title: "Transformative Trailblazers",
    description:
      "You're well-positioned to drive meaningful action, and likely bring initatives of your own.",
    focus: "Maximizing impact through leadership and collaboration",
    actionLevels: {
      spark: "ready_to_lead",
      sculpt: "ready_to_lead",
      steward: "ready_to_lead",
    },
  },
}

function getRecommendationsForPersona(levels: PersonaLevel) {
  // Find activities that match the persona's levels
  const matchingActivities = participationActivities.activities
    .filter((activity) =>
      Object.entries(levels).every(([dimension, level]) =>
        activity.requirements[dimension as keyof ActivityRequirements].includes(
          level
        )
      )
    )
    .map((activity) => activity.text)
    // Limit to 3 activities
    .slice(0, 3)

  return matchingActivities
}

export function PersonaQuiz() {
  const [questionIndex, setQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<
    Record<string, { primary: number; secondary: number }>
  >({})
  const [showResults, setShowResults] = useState(false)
  const [persona, setPersona] = useState<string | null>(null)
  const [isSecondary, setIsSecondary] = useState(false)

  const getDimensionLevel = (
    primary: number,
    secondary: number,
    weights: { primary: number; secondary: number }
  ) => {
    const weightedScore =
      primary * weights.primary + secondary * weights.secondary
    return weightedScore >= 2.5 ? "high" : "low"
  }

  const handleAnswer = (score: number) => {
    const currentQuestion = questions[questionIndex]
    const updatedAnswers = { ...answers }

    if (!isSecondary) {
      // Primary question
      updatedAnswers[currentQuestion.dimension] = {
        ...updatedAnswers[currentQuestion.dimension],
        primary: score,
      }
      setAnswers(updatedAnswers)
      setIsSecondary(true)
    } else {
      // Secondary question
      updatedAnswers[currentQuestion.dimension] = {
        ...updatedAnswers[currentQuestion.dimension],
        secondary: score,
      }
      setAnswers(updatedAnswers)

      if (questionIndex >= questions.length - 1) {
        // Calculate final persona
        const levels = {
          motivation: getDimensionLevel(
            updatedAnswers.motivation.primary,
            updatedAnswers.motivation.secondary,
            questions[0].weights
          ),
          capability: getDimensionLevel(
            updatedAnswers.capability.primary,
            updatedAnswers.capability.secondary,
            questions[1].weights
          ),
          opportunity: getDimensionLevel(
            updatedAnswers.opportunity.primary,
            updatedAnswers.opportunity.secondary,
            questions[2].weights
          ),
        }

        const key = `${levels.motivation}-${levels.capability}-${levels.opportunity}`
        setPersona(key)
        setShowResults(true)
      } else {
        setQuestionIndex(questionIndex + 1)
        setIsSecondary(false)
      }
    }
  }

  const resetQuiz = () => {
    setQuestionIndex(0)
    setAnswers({})
    setShowResults(false)
    setPersona(null)
    setIsSecondary(false)
  }

  const goBack = () => {
    if (isSecondary) {
      setIsSecondary(false)
    } else if (questionIndex > 0) {
      setQuestionIndex(questionIndex - 1)
      setIsSecondary(true)
    }
  }

  if (showResults && persona) {
    const recommendation = personaRecommendations[persona]
    const personaName = {
      "low-low-low": "Skeptical Spectators",
      "high-low-low": "Eager Explorers",
      "low-high-low": "Latent Luminaries",
      "high-high-low": "Capable Catalysts",
      "low-low-high": "Watchful Wardens",
      "high-low-high": "Aspiring Accelerators",
      "low-high-high": "Dormant Dynamos",
      "high-high-high": "Transformative Trailblazers",
    }[persona]

    return (
      <div className="rounded-lg border border-blue-200 bg-blue-50/30 p-6 dark:border-blue-900/50 dark:bg-blue-900/20">
        <h3 className="mt-0">Your Innovation Journey</h3>
        <p>
          Based on your responses, you might align with our{" "}
          <span className="font-semibold">"{personaName}"</span> persona.
        </p>

        <div className="mt-6 space-y-6">
          <p className="text-muted-foreground">{recommendation.description}</p>
          <p className="text-sm text-muted-foreground">
            Focus: {recommendation.focus}
          </p>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {Object.entries(recommendation.actionLevels).map(
              ([action, level]) => (
                <div
                  key={action}
                  className={cn("rounded-lg border p-6", {
                    "border-amber-200 bg-amber-50/30 dark:border-amber-900/50 dark:bg-amber-900/20":
                      action === "spark",
                    "border-purple-200 bg-purple-50/30 dark:border-purple-900/50 dark:bg-purple-900/20":
                      action === "sculpt",
                    "border-emerald-200 bg-emerald-50/30 dark:border-emerald-900/50 dark:bg-emerald-900/20":
                      action === "steward",
                  })}
                >
                  <div className="mb-4 flex items-center gap-3">
                    {action === "spark" && (
                      <IconFlame className="h-8 w-8 text-amber-600 dark:text-amber-400" />
                    )}
                    {action === "sculpt" && (
                      <IconTools className="h-8 w-8 text-purple-600 dark:text-purple-400" />
                    )}
                    {action === "steward" && (
                      <IconCompass className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
                    )}
                    <div className="flex w-full items-center justify-between">
                      <h3 className="m-0 capitalize">{action}</h3>
                      <div className="flex items-center">
                        <span
                          className={cn(
                            "inline-flex select-none items-center justify-center whitespace-pre-line rounded-full px-3 py-1.5 text-center text-xs font-medium leading-tight",
                            {
                              "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300":
                                level === "starting_out",
                              "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300":
                                level === "ready_to_collaborate",
                              "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300":
                                level === "ready_to_lead",
                            }
                          )}
                        >
                          {actionLevelLabels[level]}
                        </span>
                      </div>
                    </div>
                  </div>
                  <p className="mb-3 text-sm text-muted-foreground">
                    {actionSetDescriptions[action as ActionSet]}
                  </p>
                  <ul className="space-y-2 text-sm">
                    {actionSetContent[action as ActionSet][level].map(
                      (actionItem, index) => (
                        <li key={index}>{actionItem}</li>
                      )
                    )}
                  </ul>
                </div>
              )
            )}
          </div>
        </div>

        <div className="mt-6 flex gap-4">
          <button
            onClick={resetQuiz}
            className="inline-flex items-center rounded-md border border-blue-600 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-blue-500 dark:text-blue-500 dark:hover:bg-blue-900/20"
          >
            Retake Quiz
          </button>
          <Link
            href="/model/innovation-ecosystem"
            className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:hover:bg-blue-600"
          >
            Learn More About Personas →
          </Link>
        </div>
      </div>
    )
  }

  const currentQuestion = questions[questionIndex]
  const currentQuestionData = isSecondary
    ? currentQuestion.secondary
    : currentQuestion.primary
  const questionNumber = questionIndex * 2 + (isSecondary ? 2 : 1)
  const totalQuestions = questions.length * 2

  return (
    <div className="rounded-lg border border-blue-200 bg-blue-50/30 p-6 dark:border-blue-900/50 dark:bg-blue-900/20">
      <h3 className="mt-0">{currentQuestionData.text}</h3>
      <div className="mt-4 space-y-3">
        {currentQuestionData.options.map((option, index) => (
          <button
            key={index}
            onClick={() => handleAnswer(option.score)}
            className="w-full rounded-lg border border-blue-200 bg-white p-4 text-left hover:bg-blue-50 dark:border-blue-800 dark:bg-black/40 dark:hover:bg-blue-900/40"
          >
            {option.text}
          </button>
        ))}
      </div>
      <div className="mt-4 flex justify-between text-sm text-muted-foreground">
        <span>
          Question {questionNumber} of {totalQuestions}
        </span>
        {(questionIndex > 0 || isSecondary) && (
          <button
            onClick={goBack}
            className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            ← Previous Question
          </button>
        )}
      </div>
    </div>
  )
}
