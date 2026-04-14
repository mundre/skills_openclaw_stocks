# Input Schema

Use a JSON file with this structure.

```json
{
  "candidate": {
    "name": "Alex Chen",
    "contact_line": "alex@example.com | +1 555-0100 | Singapore | CET-6",
    "base_summary": "Optional general summary used as source material."
  },
  "style": {
    "latin_font": "Times New Roman",
    "cjk_font": "宋体"
  },
  "education": [
    {
      "left": "Example University | MBA",
      "right": "2022.09 - 2024.06",
      "bullets": [
        "Relevant coursework or achievements.",
        "Language or collaboration context."
      ]
    }
  ],
  "experience": [
    {
      "key": "media_assistant",
      "default_left": "Project Coordinator | Example Media Co.",
      "default_right": "2024.01 - Present",
      "default_bullets": [
        "Base bullets used when no track override exists."
      ]
    }
  ],
  "campus": [
    {
      "left": "Business Simulation Project",
      "right": "Graduate Program",
      "bullets": [
        "Optional campus or extracurricular item."
      ]
    }
  ],
  "tracks": {
    "operations": {
      "title": "Operations Coordinator / Platform Operations",
      "summary": "Role-targeted summary.",
      "experience_order": ["media_assistant"],
      "experience_overrides": {
        "media_assistant": {
          "left": "Operations Assistant | Example Media Co.",
          "right": "2024.01 - Present",
          "bullets": [
            "Track-specific rewrite."
          ]
        }
      },
      "campus_items": [
        {
          "left": "Business Simulation Project",
          "right": "Graduate Program",
          "bullets": [
            "Track-specific campus rewrite."
          ]
        }
      ],
      "skills_lines": [
        "Tools: Excel, PowerPoint, Photoshop.",
        "Keywords: coordination, documentation, scheduling."
      ]
    }
  }
}
```

## Required fields

- `candidate.name`
- `candidate.contact_line`
- `education`
- `tracks`

## Track behavior

Each track creates a separate resume version.

- `experience_order` determines ordering
- `experience_overrides` lets you rewrite bullets per track
- if a role is not overridden, the generator falls back to `default_*`

## Filename behavior

The script uses:

- candidate name
- track key

and sanitizes the result to a safe filename.

