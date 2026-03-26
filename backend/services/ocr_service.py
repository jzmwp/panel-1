"""OCR service — Claude Vision classifies and extracts data from any scanned mine report."""

import base64
import io
import json
import logging
import mimetypes

import anthropic
from PIL import Image

from backend.config import settings

MAX_IMAGE_BYTES = 4_500_000  # stay under Claude's 5MB limit


def _prepare_image(filepath: str) -> tuple[str, str]:
    """Read an image file and resize if needed to stay under Claude's 5MB limit.
    Returns (base64_data, mime_type)."""
    mime_type = mimetypes.guess_type(filepath)[0] or "image/jpeg"

    with open(filepath, "rb") as f:
        raw = f.read()

    # If already small enough and a supported type, use as-is
    if len(raw) <= MAX_IMAGE_BYTES and mime_type in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        return base64.b64encode(raw).decode("utf-8"), mime_type

    # Resize using Pillow
    img = Image.open(io.BytesIO(raw))

    # Convert RGBA/palette to RGB for JPEG
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    # Progressively shrink until under limit
    quality = 85
    for scale in [1.0, 0.75, 0.5, 0.35, 0.25]:
        w, h = int(img.width * scale), int(img.height * scale)
        resized = img.resize((w, h), Image.LANCZOS) if scale < 1.0 else img

        buf = io.BytesIO()
        resized.save(buf, format="JPEG", quality=quality, optimize=True)
        data = buf.getvalue()

        if len(data) <= MAX_IMAGE_BYTES:
            logger.info(f"Image resized: {len(raw)} -> {len(data)} bytes ({w}x{h}, q={quality})")
            return base64.b64encode(data).decode("utf-8"), "image/jpeg"

        quality = max(quality - 10, 50)

    # Last resort: very small
    resized = img.resize((int(img.width * 0.2), int(img.height * 0.2)), Image.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format="JPEG", quality=50)
    data = buf.getvalue()
    return base64.b64encode(data).decode("utf-8"), "image/jpeg"

logger = logging.getLogger(__name__)

CLASSIFY_AND_EXTRACT_PROMPT = """You are an expert at reading underground coal mine operational documents — both digital forms and handwritten reports.

Look at this scanned document and do TWO things:

## 1. CLASSIFY IT
Determine what type of mine report this is. Common types:
- shift_statutory_report (deputy's statutory inspection — gas readings, strata conditions, ventilation, abnormal indications)
- longwall_production_report (shift production — shears, metres, tonnes, delays, equipment status, face conditions)
- strata_assessment (convergence readings, roof/rib/floor conditions, TARP levels, faulting)
- gas_monitoring (dedicated gas readings log — CH4, CO, O2, CO2, NO2, H2S at various locations)
- ventilation_reading (air velocity, air quantity, temperatures, pressures)
- hazard_report (identified hazards, severity, likelihood, actions)
- incident_report (incidents, near-misses, injuries)
- tarp_activation (trigger action response plan — trigger level, actions taken)
- equipment_log (breakdown, maintenance, repair records)
- prestart_checklist (pre-start equipment checks)
- other (describe it)

## 2. EXTRACT ALL DATA
Extract every piece of information you can read from the document into a flat JSON object. Use descriptive field names in snake_case.

For common fields, always use these exact names:
- report_date (YYYY-MM-DD format)
- shift (day/afternoon/night, or A/B/C/D)
- panel (e.g. LW101, LW104)
- submitted_by (person who filled it in)
- crew (crew identifier)

For everything else, use descriptive names based on what the field represents. For gas readings at multiple locations, use arrays. For tables (like production delays), use arrays of objects.

Read handwriting carefully. Common abbreviations: MG=maingate, TG=tailgate, CT=cut-through, UM=undermanager, ERZ=explosion risk zone, SOP=standard operating procedure, TARP=trigger action response plan, VFI=ventilation flow indicator, SCARIN=strata control and reinforcement inspection, PUR=powered unrestricted roof, MCT=mean cycle time.

If a value is illegible, set it to null. Don't guess.

## RESPONSE FORMAT
Return ONLY valid JSON in this exact structure:
{
  "report_category": "the_category_from_above",
  "report_category_label": "Human-readable label e.g. Shift Statutory Report",
  "confidence": 0.0 to 1.0,
  "fields": {
    "report_date": "YYYY-MM-DD",
    "shift": "...",
    "panel": "...",
    "submitted_by": "...",
    ...all other extracted fields...
  }
}"""


async def classify_and_extract(filepath: str) -> dict:
    """Use Claude Vision to classify and extract data from any scanned mine report."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    image_data, mime_type = _prepare_image(filepath)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": CLASSIFY_AND_EXTRACT_PROMPT,
                    },
                ],
            }
        ],
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
        logger.error(f"Failed to parse extraction JSON: {raw_text[:500]}")
        result = {
            "report_category": "unknown",
            "report_category_label": "Unknown",
            "confidence": 0.0,
            "fields": {},
        }

    return {
        "report_category": result.get("report_category", "unknown"),
        "report_category_label": result.get("report_category_label", "Unknown"),
        "confidence": result.get("confidence", 0.0),
        "fields": result.get("fields", {}),
        "raw_text": raw_text,
    }
