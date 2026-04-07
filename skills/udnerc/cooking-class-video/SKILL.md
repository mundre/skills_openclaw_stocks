---
name: cooking-class-video
version: 1.0.0
displayName: Cooking Class Video Maker
description: |
  A great cooking class smells like garlic hitting a hot pan and sounds like someone saying "I can't believe I made that." None of that survives a text description. Cooking Class Video turns your knife skills workshop, pasta-making evening, or professional pastry course into a short video where the food looks real, the instructor looks approachable, and the signup link actually gets clicked.

  Create a cooking school enrollment video, knife skills class promo, baking and pastry course ad, date night cooking class marketing video, kids cooking camp highlight, professional culinary program overview, or private chef lesson explainer — for recreational cooks or aspiring professionals.

  **Use Cases**
  - Valentine's Day and date night cooking class promotion
  - Kids summer cooking camp enrollment video
  - Professional culinary certificate program recruitment
  - Corporate team-building cooking event marketing

  **How It Works**
  Tell the AI your class format, cuisine style, skill level, and what students walk away able to cook. The AI writes a sensory, appetite-driven script and produces a video that makes people hungry to sign up.

  **Example**
  ```bash
  curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
    -H "Authorization: Bearer $NEMO_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "skill": "cooking-class-video",
      "inputs": {
        "class_name": "The Artisan Kitchen",
        "style": "Italian, French, and Asian fusion",
        "format": "hands-on evening classes, max 12 students",
        "outcome": "students cook and eat a 3-course meal every session"
      }
    }'
  ```
metadata:
  openclaw.emoji: "👨‍🍳"
  openclaw.requires: ["NEMO_TOKEN"]
  openclaw.primaryEnv: NEMO_TOKEN
  configPaths: ["~/.config/nemovideo/"]
---

# Cooking Class Video

The sizzle of garlic hitting a hot pan, hands shaping fresh pasta, strangers laughing over food they made together. This skill creates promo videos for cooking schools and culinary studios.

What It Does

- Class overview and experience video for online booking pages
- Chef instructor introduction and credential showcase
- Gift experience promo for date nights and team building
- Multi-week course enrollment video for serious culinary students

How to Use

Describe the class type, format, group size, and what students leave with.

Example: Create a promo video for Saturday pasta-making class at Forno Kitchen Studio. Groups of 8, 3 hours hands-on, everyone eats what they make, wine included.

Tips

Use sensory language in the first 5 seconds. Feature the moment students take their first bite of something they made.