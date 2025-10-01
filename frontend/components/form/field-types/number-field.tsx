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

interface NumberFieldProps {
  field: FormFieldConfig
}

export function NumberField({ field }: NumberFieldProps) {
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
              type="number"
              placeholder={field.placeholder}
              min={field.min}
              max={field.max}
              {...formField}
              onChange={(e) => {
                const value = e.target.value === "" ? "" : Number(e.target.value)
                formField.onChange(value)
              }}
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
