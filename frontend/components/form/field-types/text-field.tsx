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

interface TextFieldProps {
  field: FormFieldConfig
}

export function TextField({ field }: TextFieldProps) {
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
              type="text"
              placeholder={field.placeholder}
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
