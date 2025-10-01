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
import { Checkbox } from "@/components/ui/checkbox"
import type { FormField as FormFieldConfig } from "@/lib/schemas/field-to-zod"

interface CheckboxFieldProps {
  field: FormFieldConfig
}

export function CheckboxField({ field }: CheckboxFieldProps) {
  const form = useFormContext()

  return (
    <FormField
      control={form.control}
      name={field.key}
      render={({ field: formField }) => (
        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
          <FormControl>
            <Checkbox
              checked={formField.value}
              onCheckedChange={formField.onChange}
            />
          </FormControl>
          <div className="space-y-1 leading-none">
            <FormLabel>
              {field.label || field.key}
              {field.required && <span className="text-destructive ml-1">*</span>}
            </FormLabel>
            {field.description && (
              <FormDescription>{field.description}</FormDescription>
            )}
            <FormMessage />
          </div>
        </FormItem>
      )}
    />
  )
}
