"use client"

import { useMemo } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Form } from "@/components/ui/form"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { FieldRenderer } from "./field-renderer"
import { useResumeRun } from "@/lib/hooks/use-resume-run"
import {
  fieldConfigToZodSchema,
  generateDefaultValues,
  type FormField,
} from "@/lib/schemas/field-to-zod"
import { Loader2, AlertCircle } from "lucide-react"

interface DynamicFormProps {
  runId: string
  fields: FormField[]
  onSuccess?: (data: unknown) => void
  onError?: (error: Error) => void
}

/**
 * Dynamic form component that generates form fields from backend config
 * Handles validation, submission, and API integration automatically
 *
 * Features:
 * - Auto-generates Zod schema from field config
 * - Live validation with error display
 * - Disabled state during submission
 * - Success/error callbacks
 * - Accessible labels and error messages
 *
 * @param runId - The run ID to resume
 * @param fields - Array of form field configurations from backend
 * @param onSuccess - Optional callback on successful submission
 * @param onError - Optional callback on error
 *
 * @example
 * ```tsx
 * <DynamicForm
 *   runId="run_123"
 *   fields={[
 *     { key: "email", type: "email", required: true },
 *     { key: "age", type: "number", required: true, min: 18, max: 120 }
 *   ]}
 *   onSuccess={() => router.push(`/runs/${runId}`)}
 *   onError={(err) => toast.error(err.message)}
 * />
 * ```
 */
export function DynamicForm({ runId, fields, onSuccess, onError }: DynamicFormProps) {
  // Generate Zod schema from field config
  const schema = useMemo(() => fieldConfigToZodSchema(fields), [fields])

  // Generate default values
  const defaultValues = useMemo(() => generateDefaultValues(fields), [fields])

  // Initialize form with Zod resolver
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues,
  })

  // Resume run mutation
  const resumeRun = useResumeRun()

  // Form submission handler
  const onSubmit = async (values: Record<string, unknown>) => {
    try {
      const result = await resumeRun.mutateAsync({
        runId,
        inputs: values,
      })
      onSuccess?.(result)
    } catch (error) {
      const err = error instanceof Error ? error : new Error("Unknown error occurred")
      onError?.(err)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Error Alert */}
        {resumeRun.error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {resumeRun.error instanceof Error
                ? resumeRun.error.message
                : "An error occurred while submitting the form"}
            </AlertDescription>
          </Alert>
        )}

        {/* Dynamic Fields */}
        <div className="space-y-4">
          {fields.map((field) => (
            <FieldRenderer key={field.key} field={field} />
          ))}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-2">
          <Button
            type="submit"
            disabled={resumeRun.isPending || form.formState.isSubmitting}
          >
            {resumeRun.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {resumeRun.isPending ? "Submitting..." : "Submit"}
          </Button>
        </div>
      </form>
    </Form>
  )
}
