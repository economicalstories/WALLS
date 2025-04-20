"use client"

import React from "react"
import { useMediaQuery } from "usehooks-ts"
import { BiLogoLinkedinSquare } from "react-icons/bi"
import Image from "next/image"

type SteeringCommitteeMember = {
  name: string
  role: string
  organization: string
  image: string
  bio: string
  socialLinks?: { href: string; icon: React.ReactNode }[]
}

type Props = {
  tagline: string
  heading: string
  description: string
  members: SteeringCommitteeMember[]
}

export type SteeringCommitteeProps = React.ComponentPropsWithoutRef<"section"> &
  Partial<Props>

const SteeringCommitteeMember = ({
  member,
  className,
}: {
  member: SteeringCommitteeMember
  className?: string
}) => {
  return (
    <div className={`flex w-full flex-col text-center ${className}`}>
      <div className="rb-5 -mb-2 flex w-full items-center justify-center">
        <Image
          src={member.image}
          alt={member.name}
          width={120}
          height={120}
          className="size-[120px] min-h-[120px] min-w-[120px] rounded-full object-cover"
        />
      </div>
      <div className="relative w-full rounded-xl">
        <div
          className="absolute inset-0 rounded-xl"
          style={{
            background: `radial-gradient(closest-side, var(--background) calc(100% - 16px), transparent 100%)`,
            opacity: 0.6,
          }}
        />
        <div
          className="absolute inset-0 rounded-xl"
          style={{
            backdropFilter: `blur(4px)`,
            WebkitMaskImage: `radial-gradient(closest-side, black calc(100% - 16px), transparent 100%)`,
            maskImage: `radial-gradient(closest-side, black calc(100% - 16px), transparent 100%)`,
          }}
        />
        <div className="relative w-full rounded-xl p-4">
          <h5 className="text-md mb-1 font-semibold md:text-lg">
            {member.name}
          </h5>
          <h6 className="mb-3 text-sm text-muted-foreground md:mb-4 md:text-base">
            {member.role} • {member.organization}
          </h6>
          <p className="text-[13px] leading-relaxed text-muted-foreground md:text-sm">
            {member.bio}
          </p>
          {member.socialLinks && (
            <div className="mt-4 grid grid-flow-col grid-cols-[max-content] gap-3.5 self-center">
              {member.socialLinks.map((link, linkIndex) => (
                <a key={linkIndex} href={link.href}>
                  {link.icon}
                </a>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const shouldAddMarginTop = (index: number) => {
  return index === 1 || index === 3 || index === 7
}

const shouldAddAnotherDiv = (index: number, totalMembers: number) => {
  // Calculate if member should be on left or right side
  const isLeftSide = index % 2 === 0
  const isRightSide = index % 2 === 1

  // Add spacing divs to maintain side positioning
  return isLeftSide || (isRightSide && index < totalMembers - 1)
}

export function SteeringCommittee(props: SteeringCommitteeProps) {
  const { tagline, heading, description, members } = {
    tagline: "Our Leadership",
    heading: "Steering Committee",
    description:
      "Our Steering Committee brings together leaders from different sectors who guide our strategic direction and ensure we stay true to our mission.",
    members: [],
    ...props,
  }

  const isMobile = useMediaQuery("(max-width: 767px)")

  // Create a daily-changing but stable order
  const stableMembers = React.useMemo(() => {
    // Get today's date as a number (changes daily but stable within a day)
    const today = new Date()
    const dateNumber =
      today.getFullYear() * 10000 +
      (today.getMonth() + 1) * 100 +
      today.getDate()

    return [...members].sort((a, b) => {
      // Create a hash from member properties and today's date
      const hashA = (a.name.length * dateNumber) % 100
      const hashB = (b.name.length * dateNumber) % 100
      return hashA - hashB
    })
  }, [members])

  // Split members into left and right columns using stable sort
  const leftColumnMembers = stableMembers.filter((_, i) => i % 2 === 0)
  const rightColumnMembers = stableMembers.filter((_, i) => i % 2 === 1)

  // Generate margins that change daily but remain stable within a day
  const getMemberMargin = React.useCallback(
    (member: SteeringCommitteeMember) => {
      const today = new Date()
      const dateNumber =
        today.getFullYear() * 10000 +
        (today.getMonth() + 1) * 100 +
        today.getDate()

      // Create a hash from member name and date
      const hash = (member.name.length * dateNumber) % 5
      const margins = [0, 8, 16, 24, 32]
      return margins[hash]
    },
    []
  )

  return (
    <section className="px-[5%] py-16 md:py-24 lg:py-28">
      <div className="relative">
        {/* Title section */}
        <div className="static top-[50vh] mx-auto mt-20 max-w-lg translate-y-[-50%] text-center md:sticky">
          <div className="relative">
            <p className="mb-3 font-semibold text-muted-foreground md:mb-4">
              {tagline}
            </p>
            <h2 className="rb-5 mb-5 text-4xl font-bold md:mb-6 md:text-5xl lg:text-6xl">
              {heading}
            </h2>
            <p className="text-muted-foreground md:text-lg">{description}</p>
          </div>
        </div>

        {/* Members grid */}
        <div className="relative z-10 mx-auto mt-12 max-w-[1600px]">
          {isMobile ? (
            // Mobile layout - single column
            <div className="grid grid-cols-1 gap-8">
              {stableMembers.map((member, index) => (
                <SteeringCommitteeMember key={member.name} member={member} />
              ))}
            </div>
          ) : (
            // Desktop layout - three columns with empty middle
            <div className="grid grid-cols-[2fr_1fr_2fr] items-start gap-16">
              {/* Left column */}
              <div className="grid gap-12">
                {leftColumnMembers.map((member) => (
                  <SteeringCommitteeMember
                    key={member.name}
                    member={member}
                    className={`mt-${getMemberMargin(member)}`}
                  />
                ))}
              </div>

              {/* Middle column - empty for title */}
              <div className="min-h-[1px]" />

              {/* Right column */}
              <div className="grid gap-12">
                {rightColumnMembers.map((member) => (
                  <SteeringCommitteeMember
                    key={member.name}
                    member={member}
                    className={`mt-${getMemberMargin(member)}`}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
