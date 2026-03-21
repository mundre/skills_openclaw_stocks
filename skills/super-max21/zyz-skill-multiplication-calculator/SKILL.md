---
name: multiplication-cal
description: A tool to calculate the product of two or more numbers. Supports integers and decimals.
---

# Input JSON Schema
input_schema:
  type: object
  properties:
    numbers:
      type: array
      items:
        type: number
      minItems: 2
      description: List of numbers to multiply
  required:
    - numbers

# Output JSON Schema
output_schema:
  type: number
  description: The final product of all input numbers

# Examples
examples:
  - input:
      numbers: [5, 8]
    output: 40

  - input:
      numbers: [2.5, 4, 6]
    output: 60

  - input:
      numbers: [10, 0.3, 7]
    output: 21