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
import { Input } from "@/components/ui/input"
import type { FormField as FormFieldConfig } from "@/lib/schemas/field-to-zod"

interface EmailFieldProps {
  field: FormFieldConfig
}

export function EmailField({ field }: EmailFieldProps) {
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
            <Input
              type="email"
              placeholder={field.placeholder || "email@example.com"}
              {...formField}
            />
          </FormControl>
          {field.description && (
            <FormDescription>{field.description}</FormDescription>
          )}
          <FormMessage />
        </FormItem>
      )}
    />
  )
}
