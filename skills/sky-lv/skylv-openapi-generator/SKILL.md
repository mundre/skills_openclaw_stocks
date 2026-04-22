---
name: skylv-openapi-generator
slug: skylv-openapi-generator
version: 1.0.0
description: "Generates OpenAPI 3.0 specs from code. Creates API documentation for REST endpoints. Triggers: openapi spec, generate api doc, swagger."
author: SKY-lv
license: MIT
tags: [automation, tools]
keywords: [automation, tools]
triggers: openapi-generator
---

# OpenAPI Generator

## Overview
Creates OpenAPI 3.0 specifications for REST APIs.

## When to Use
- User asks to "generate API documentation"
- Documenting new API endpoints

## Template Structure

openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema: { type: integer }
      responses:
        200:
          description: Success

## Tips
- Always specify response schemas
- Use $ref to avoid duplication
- Group endpoints with tags
- Add examples for request/response bodies
