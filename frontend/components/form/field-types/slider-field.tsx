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
import { Slider } from "@/components/ui/slider"
import type { FormField as FormFieldConfig } from "@/lib/schemas/field-to-zod"

interface SliderFieldProps {
  field: FormFieldConfig
}

export function SliderField({ field }: SliderFieldProps) {
  const form = useFormContext()

  return (
    <FormField
      control={form.control}
      name={field.key}
      render={({ field: formField }) => (
        <FormItem>
          <div className="flex items-center justify-between">
            <FormLabel>
              {field.label || field.key}
              {field.required && <span className="text-destructive ml-1">*</span>}
            </FormLabel>
            <span className="text-muted-foreground text-sm">
              {formField.value ?? field.min ?? 0}
            </span>
          </div>
          <FormControl>
            <Slider
              min={field.min ?? 0}
              max={field.max ?? 100}
              step={1}
              value={[formField.value ?? field.min ?? 0]}
              onValueChange={(vals) => formField.onChange(vals[0])}
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
