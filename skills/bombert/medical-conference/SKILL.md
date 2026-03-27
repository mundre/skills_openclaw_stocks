---
name: medical-conference-search
description: "Search medical conference and presentation databases. Use this skill whenever the user asks about medical conferences, academic conferences, session abstracts, posters, oral presentations, or conference-presented drug/trial data. The skill runs a two-step chained workflow: first query conferences, then query presentations for rich abstract/efficacy/safety content. Trigger words include: conference, symposium, congress, ASCO, ESMO, AHA, ACC, session, abstract, poster, oral presentation, data presented at, efficacy data, safety data, congress abstract."
---

# Conference Search Skill

This skill converts natural language questions into structured API queries against a conference and presentation database, then presents the results in a readable format.

## Workflow

1. **Parse user intent** — Extract key entities from the user's question
2. **Build query parameters** — Map entities to the conference and presentation schemas
3. **Execute the query** — Run `scripts/search.py`
4. **Present results** — Format and display conferences and presentations to the user

The skill runs in **two chained steps**: first query conferences, then query presentations using the result. Always run both steps in sequence for complete results.

```
Step 1 → Query conferences        → obtain conference_name / series_name
Step 2 → Query presentations      → get abstracts, efficacy, safety, drug data
```

---

## Step 1: Conference Query Parameters

Identify the following entity types from the user's question:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `conference_name` | `str` | Full or partial conference name | `"ASCO Annual Meeting 2024"` |
| `conference_start_date` | `str` | Start date (YYYY-MM-DD) | `"2024-06-01"` |
| `conference_end_date` | `str` | End date (YYYY-MM-DD) | `"2024-06-05"` |
| `conference_location` | `str` | City, country, or venue | `"Chicago"` |
| `series_name` | `str` | Conference series name | `"ASCO"` |
| `series_organization` | `str` | Organizing body | `"American Society of Clinical Oncology"` |
| `series_area` | `List[str]` | Therapeutic or subject area(s) | `["oncology", "cardiology"]` |
| `from_n` | `int` | Pagination offset (0-based) | `0` |
| `size` | `int` | Results per page (1–10) | `10` |

**Type rules:**
- All fields except `series_area` → plain `str`
- `series_area` → `List[str]`
- Default: `from_n: 0, size: 10`

**Conference result fields returned:**
`conference_name`, `conference_abbreviation`, `conference_website`, `conference_description`, `conference_start_date`, `conference_end_date`, `conference_location`, `series_id`, `series_name`, `series_abbreviation`, `series_website`, `series_organization`, `series_area`

---

## Step 2: Presentation Query Parameters

Identify the following entity types from the user's question:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `authors` | `List[str]` | Presenter / author name(s) | `["John Smith"]` |
| `institutions` | `List[str]` | Author institution(s) | `["MD Anderson"]` |
| `drugs` | `List[str]` | Drug name(s) | `["pembrolizumab"]` |
| `diseases` | `List[str]` | Disease / indication(s) | `["lung cancer", "NSCLC"]` |
| `targets` | `List[str]` | Biological target(s) | `["PD-1", "VEGF"]` |
| `conference_name` | `str` | Auto-filled from Step 1, or provide directly | `"2024 ASCO Annual Meeting"` |
| `series_name` | `str` | Conference series name | `"ASCO"` |
| `from_n` | `int` | Pagination offset (0-based) | `0` |
| `size` | `int` | Results per page (1–5) | `5` |

**Type rules:**
- `authors`, `institutions`, `drugs`, `diseases`, `targets` → `List[str]`
- `conference_name`, `series_name` → plain `str`
- Default: `from_n: 0, size: 5`
- In chained mode (both `--conference-params` and `--presentation-params` provided), `conference_name` from the top Step 1 result is **automatically injected** into Step 2

**Presentation result fields returned:**
`session_title`, `presentation_title`, `presentation_website`, `main_author`, `main_author_institution`, `authors`, `institutions`, `abstract`, `design`, `efficacy`, `safety`, `summary`, `drugs`, `diseases`, `targets`, `series_name`, `conference_name`

---

## Step 3: Execute the Query

```bash
# Chained mode (Step 1 + Step 2, conference_name auto-injected)
python scripts/search.py --conference-params '<JSON>' --presentation-params '<JSON>'

# Step 1 only
python scripts/search.py --conference-params '<JSON>' --step conference

# Step 2 only (when conference_name is already known)
python scripts/search.py --presentation-params '<JSON>' --step presentation
```

Add `--raw` to receive the unformatted JSON response.

---

## Step 4: Interpret Results

The response contains:
- Conference fields: name, dates, location, series, organization, and area
- Presentation fields: abstract, design, efficacy, safety, drug and disease details

If results exceed 100, prompt the user to narrow the query. If no results are returned, suggest relaxing one or more filters.

---

## Conversion Examples

**User:** "What PD-1 drug data was presented at ASCO 2024?"

**Parameters:**
```bash
python scripts/search.py \
  --conference-params '{"series_name": "ASCO", "conference_start_date": "2024-01-01", "conference_end_date": "2024-12-31"}' \
  --presentation-params '{"targets": ["PD-1"]}'
```

*(`conference_name` from Step 1 is auto-injected into Step 2)*

---

**User:** "Pembrolizumab lung cancer abstracts from ESMO"

**Parameters:**
```bash
python scripts/search.py \
  --presentation-params '{"drugs": ["pembrolizumab"], "diseases": ["lung cancer"], "series_name": "ESMO"}' \
  --step presentation
```

---

**User:** "Oncology conferences in Chicago 2024"

**Parameters:**
```bash
python scripts/search.py \
  --conference-params '{"series_area": ["oncology"], "conference_location": "Chicago", "conference_start_date": "2024-01-01", "conference_end_date": "2024-12-31"}' \
  --step conference
```

---

**User:** "KRAS G12C presentations by MD Anderson researchers"

**Parameters:**
```bash
python scripts/search.py \
  --presentation-params '{"targets": ["KRAS G12C"], "institutions": ["MD Anderson"]}' \
  --step presentation
```

---

**User:** "Roche bispecific antibody data at hematology conferences"

**Parameters:**
```bash
python scripts/search.py \
  --conference-params '{"series_area": ["hematology"]}' \
  --presentation-params '{"drugs": ["bispecific antibody"], "institutions": ["Roche"]}'
```

---

## Dependencies

- Python 3.8+
- `requests` library (`pip install requests`)
- Environment variable `NOAH_API_TOKEN` — API authentication token (required)
  - Register for a free account at [noah.bio](https://noah.bio) to obtain your API key.
