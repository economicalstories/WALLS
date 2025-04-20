"use client"

import {
  Breadcrumb as RelumeBreakcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@relume_io/relume-ui"

interface BreadcrumbItemType {
  label: string
  href?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItemType[]
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <RelumeBreakcrumb>
      <BreadcrumbList>
        {items.map((item, index) => (
          <BreadcrumbItem key={index}>
            {index === items.length - 1 ? (
              <BreadcrumbPage>{item.label}</BreadcrumbPage>
            ) : (
              <BreadcrumbLink href={item.href}>{item.label}</BreadcrumbLink>
            )}
            {index < items.length - 1 && <BreadcrumbSeparator />}
          </BreadcrumbItem>
        ))}
      </BreadcrumbList>
    </RelumeBreakcrumb>
  )
}

export {
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
}
