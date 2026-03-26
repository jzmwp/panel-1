"""Document management agent — classifies, normalizes, validates, and routes documents."""

import json
import logging

import anthropic

from backend.config import settings

logger = logging.getLogger(__name__)

MANAGER_PROMPT = """You are a document management agent for an underground coal mine. Your job is to take raw extracted data from a scanned mine report and:

1. **CLASSIFY** it into an existing category, or create a new one
2. **NORMALIZE** the field names to match the category's canonical schema
3. **VALIDATE** values and flag any anomalies

## Existing Categories
{categories_context}

## Raw Extraction
Report category suggested by OCR: {raw_category}
Extracted fields:
{raw_fields}

## Your Tasks

### Task 1: Category Match
Look at the existing categories and their field schemas. Does this document match one of them?
- If YES: use that category's name and normalize the fields to match its schema
- If NO: create a new category with a descriptive name (snake_case), human label, description, and define the canonical field schema based on what you see in this document

### Task 2: Normalize Fields
Map the raw extracted fields to the canonical schema field names. If the raw data has a field like "methane_general_body" but the schema expects "ch4_general", map it. Include ALL data — don't drop fields, but use the canonical names.

### Task 3: Validate
Check values against known limits for underground coal mines:
- CH4 should be 0-5% (flag if > 2.0%)
- CO should be 0-200 ppm (flag if > 50 ppm)
- O2 should be 15-21% (flag if < 19.5%)
- CO2 should be 0-3% (flag if > 0.5%)
- Convergence rate should be 0-20 mm/day (flag if > 5 mm/day)
- Production tonnes should be 0-50000
- Shears should be 0-30

## Response Format
Return ONLY valid JSON:
{{
  "matched_existing_category": true or false,
  "category": {{
    "name": "snake_case_name",
    "label": "Human Readable Label",
    "description": "What this report type contains",
    "field_schema": {{
      "field_name": {{"type": "string|number|boolean|array|object", "label": "Human Label", "unit": "optional unit"}},
      ...
    }}
  }},
  "normalized_fields": {{
    ...all fields with canonical names...
  }},
  "validation": {{
    "flags": [
      {{"field": "field_name", "value": "the value", "issue": "description of concern", "severity": "info|warning|critical"}}
    ],
    "is_duplicate": false,
    "duplicate_reason": null
  }}
}}"""


async def manage_document(raw_category: str, raw_fields: dict, existing_categories: list[dict]) -> dict:
    """Run the document management agent on extracted data."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Build categories context
    if existing_categories:
        cats_text = ""
        for cat in existing_categories:
            schema_str = json.dumps(cat.get("field_schema", {}), indent=2)
            cats_text += f"\n### {cat['label']} (`{cat['name']}`)\n"
            cats_text += f"Description: {cat.get('description', 'N/A')}\n"
            cats_text += f"Documents: {cat.get('sample_count', 0)}\n"
            cats_text += f"Schema:\n```json\n{schema_str}\n```\n"
    else:
        cats_text = "No categories exist yet. You must create the first one."

    prompt = MANAGER_PROMPT.format(
        categories_context=cats_text,
        raw_category=raw_category or "unknown",
        raw_fields=json.dumps(raw_fields, indent=2, default=str),
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text if response.content else ""

    try:
        json_str = raw_text
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]
        result = json.loads(json_str.strip())
    except (json.JSONDecodeError, IndexError):
        logger.error(f"Document manager failed to parse: {raw_text[:500]}")
        result = {
            "matched_existing_category": False,
            "category": {
                "name": raw_category or "unknown",
                "label": raw_category or "Unknown",
                "description": "",
                "field_schema": {k: {"type": "string", "label": k} for k in raw_fields},
            },
            "normalized_fields": raw_fields,
            "validation": {"flags": [], "is_duplicate": False},
        }

    return result
