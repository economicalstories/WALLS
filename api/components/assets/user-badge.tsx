"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Typography } from "@/components/ui/typography"
import type { DirectusUser } from "@/types/directus-schema"
import { getAvatarUrl } from "@/lib/utils"

interface UserBadgeProps {
  user: DirectusUser
  size?: "sm" | "md" | "lg"
  showName?: boolean
}

export function UserBadge({
  user,
  size = "md",
  showName = true,
}: UserBadgeProps) {
  const avatarSizes = {
    sm: "h-6 w-6",
    md: "h-8 w-8",
    lg: "h-10 w-10",
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

  return (
    <div className="flex items-center gap-2">
      <Avatar className={avatarSizes[size]}>
        <AvatarImage
          src={getAvatarUrl(user.avatar)}
          alt={`${user.first_name} ${user.last_name}`}
        />
        <AvatarFallback>
          {getInitials(`${user.first_name} ${user.last_name}`)}
        </AvatarFallback>
      </Avatar>
      {showName && (
        <Typography variant="small">
          {user.first_name} {user.last_name}
        </Typography>
      )}
    </div>
  )
}
