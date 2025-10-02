import * as React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { cn } from "@/lib/utils"

interface MarkdownProps {
  children: string
  className?: string
}

/**
 * Markdown renderer with GitHub-flavored markdown support.
 *
 * Features:
 * - Tables, strikethrough, task lists (via remark-gfm)
 * - Styled with Tailwind to match shadcn/ui theme
 * - Sanitized output (react-markdown is XSS-safe by default)
 *
 * @example
 * ```tsx
 * <Markdown>
 *   {`# Heading
 *   - List item
 *   - Another item
 *
 *   **Bold text** and *italic text*`}
 * </Markdown>
 * ```
 */
export function Markdown({ children, className }: MarkdownProps) {
  return (
    <div
      className={cn(
        "prose prose-sm dark:prose-invert max-w-none",
        // Headings
        "prose-headings:font-semibold prose-headings:tracking-tight",
        "prose-h1:text-2xl prose-h1:mb-4",
        "prose-h2:text-xl prose-h2:mb-3",
        "prose-h3:text-lg prose-h3:mb-2",
        "prose-h4:text-base prose-h4:mb-2",
        // Paragraphs and text
        "prose-p:text-sm prose-p:leading-relaxed prose-p:mb-4",
        "prose-p:text-foreground",
        // Lists
        "prose-ul:list-disc prose-ul:pl-6 prose-ul:mb-4",
        "prose-ol:list-decimal prose-ol:pl-6 prose-ol:mb-4",
        "prose-li:text-sm prose-li:mb-1",
        // Links
        "prose-a:text-primary prose-a:underline prose-a:underline-offset-4",
        "hover:prose-a:text-primary/80",
        // Code
        "prose-code:text-sm prose-code:bg-muted prose-code:px-1.5 prose-code:py-0.5",
        "prose-code:rounded prose-code:font-mono prose-code:before:content-none",
        "prose-code:after:content-none",
        // Pre/code blocks
        "prose-pre:bg-muted prose-pre:border prose-pre:rounded-lg prose-pre:p-4",
        "prose-pre:overflow-x-auto prose-pre:mb-4",
        // Blockquotes
        "prose-blockquote:border-l-4 prose-blockquote:border-border",
        "prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:text-muted-foreground",
        // Tables
        "prose-table:w-full prose-table:border-collapse prose-table:mb-4",
        "prose-th:border prose-th:border-border prose-th:bg-muted/50",
        "prose-th:px-4 prose-th:py-2 prose-th:text-left prose-th:font-semibold",
        "prose-td:border prose-td:border-border prose-td:px-4 prose-td:py-2",
        // Strong/em
        "prose-strong:font-semibold prose-strong:text-foreground",
        "prose-em:italic",
        // HR
        "prose-hr:border-border prose-hr:my-6",
        className
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Task lists (checkboxes)
          input: ({ ...props }) => {
            if (props.type === "checkbox") {
              return (
                <input
                  type="checkbox"
                  disabled
                  className="mr-2 align-middle accent-primary"
                  {...props}
                />
              )
            }
            return <input {...props} />
          },
          // Ensure newlines are preserved
          p: ({ ...props }) => <p className="whitespace-pre-wrap" {...props} />,
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}
