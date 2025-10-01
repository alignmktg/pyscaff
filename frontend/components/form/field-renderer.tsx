"use client"

import type { FormField as FormFieldConfig } from "@/lib/schemas/field-to-zod"
import { TextField } from "./field-types/text-field"
import { EmailField } from "./field-types/email-field"
import { NumberField } from "./field-types/number-field"
import { TextAreaField } from "./field-types/textarea-field"
import { SelectField } from "./field-types/select-field"
import { CheckboxField } from "./field-types/checkbox-field"
import { RadioField } from "./field-types/radio-field"
import { SliderField } from "./field-types/slider-field"

interface FieldRendererProps {
  field: FormFieldConfig
}

/**
 * Renders a single form field based on its type
 * Maps field config to appropriate shadcn/ui component
 *
 * Supported field types:
 * - text: Basic text input
 * - email: Email input with validation
 * - number: Numeric input with min/max
 * - textarea: Multi-line text input
 * - select: Dropdown selection
 * - checkbox: Boolean checkbox
 * - radio: Radio button group
 * - slider: Range slider
 *
 * @example
 * ```tsx
 * <FieldRenderer field={{
 *   key: "email",
 *   type: "email",
 *   label: "Email Address",
 *   required: true
 * }} />
 * ```
 */
export function FieldRenderer({ field }: FieldRendererProps) {
  switch (field.type) {
    case "text":
      return <TextField field={field} />

    case "email":
      return <EmailField field={field} />

    case "number":
      return <NumberField field={field} />

    case "textarea":
      return <TextAreaField field={field} />

    case "select":
      return <SelectField field={field} />

    case "checkbox":
      return <CheckboxField field={field} />

    case "radio":
      return <RadioField field={field} />

    case "slider":
      return <SliderField field={field} />

    default:
      console.warn(`Unknown field type: ${field.type}. Falling back to text input.`)
      return <TextField field={field} />
  }
}
