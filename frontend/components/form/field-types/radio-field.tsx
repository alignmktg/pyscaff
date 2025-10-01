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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import type { FormField as FormFieldConfig } from "@/lib/schemas/field-to-zod"

interface RadioFieldProps {
  field: FormFieldConfig
}

export function RadioField({ field }: RadioFieldProps) {
  const form = useFormContext()

  return (
    <FormField
      control={form.control}
      name={field.key}
      render={({ field: formField }) => (
        <FormItem className="space-y-3">
          <FormLabel>
            {field.label || field.key}
            {field.required && <span className="text-destructive ml-1">*</span>}
          </FormLabel>
          <FormControl>
            <RadioGroup
              onValueChange={formField.onChange}
              defaultValue={formField.value}
              className="flex flex-col space-y-1"
            >
              {field.options?.map((option) => (
                <div key={option} className="flex items-center space-x-2">
                  <RadioGroupItem value={option} id={`${field.key}-${option}`} />
                  <Label htmlFor={`${field.key}-${option}`}>{option}</Label>
                </div>
              ))}
            </RadioGroup>
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
