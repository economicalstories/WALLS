"use client"

import * as React from "react"
import { unified } from "unified"
import remarkParse from "remark-parse"
import remarkGfm from "remark-gfm"
import remarkRehype from "remark-rehype"
import rehypeSanitize from "rehype-sanitize"
import rehypeStringify from "rehype-stringify"

import { cn } from "@/lib/utils"

interface MarkdownProps {
  content: string
  className?: string
}

export function Markdown({ content, className }: MarkdownProps) {
  const [html, setHtml] = React.useState("")

  React.useEffect(() => {
    unified()
      .use(remarkParse)
      .use(remarkGfm)
      .use(remarkRehype)
      .use(rehypeSanitize)
      .use(rehypeStringify)
      .process(content)
      .then((file) => {
        setHtml(String(file))
      })
  }, [content])

  return (
    <div
      className={cn("prose dark:prose-invert", className)}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
} 