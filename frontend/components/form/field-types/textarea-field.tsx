"use client"

import { useFormContext } from "react-hook-form"
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Textarea } from "@/components/ui/textarea"
import type { FormField as FormFieldConfig } from "@/lib/schemas/field-to-zod"

interface TextAreaFieldProps {
  field: FormFieldConfig
}

export function TextAreaField({ field }: TextAreaFieldProps) {
  const form = useFormContext()

  return (
    <FormField
      control={form.control}
      name={field.key}
      render={({ field: formField }) => (
        <FormItem>
          <FormLabel>
            {field.label || field.key}
            {field.required && <span className="text-destructive ml-1">*</span>}
          </FormLabel>
          <FormControl>
            <Textarea
              placeholder={field.placeholder}
              maxLength={field.maxLength}
              {...formField}
            />
          </FormControl>
          {field.description && (
            <FormDescription>{field.description}</FormDescription>
          )}
          {field.maxLength && (
            <p className="text-muted-foreground text-sm">
              {formField.value?.length || 0} / {field.maxLength}
            </p>
          )}
          <FormMessage />
        </FormItem>
      )}
    />
  )
}
