"""OCR service — Claude Vision classifies and extracts data from any scanned mine report."""

import base64
import io
import json
import logging
import mimetypes

import anthropic

from backend.config import settings

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

MAX_IMAGE_BYTES = 4_500_000  # stay under Claude's 5MB limit


def _enhance_for_ocr(img):
    """Pre-process a scanned document image to improve handwriting readability."""
    from PIL import ImageEnhance, ImageFilter

    # Convert to RGB if needed
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")

    # 1. Sharpen — makes fuzzy handwriting crisper
    img = img.filter(ImageFilter.SHARPEN)

    # 2. Boost contrast — separates ink from paper
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    # 3. Boost brightness slightly — lightens paper, keeps ink dark
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.1)

    # 4. Second sharpen pass for really fuzzy scans
    img = img.filter(ImageFilter.SHARPEN)

    # 5. Slight color boost — helps with faded ink
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(0.8)  # slightly desaturate — focuses on luminance contrast

    return img


def _prepare_image(filepath: str) -> tuple[str, str]:
    """Read and prepare an image for Claude Vision OCR.
    Returns (base64_data, mime_type)."""
    mime_type = mimetypes.guess_type(filepath)[0] or "image/jpeg"

    with open(filepath, "rb") as f:
        raw = f.read()

    if HAS_PIL:
        # Enhanced path: resize and sharpen with PIL
        img = Image.open(io.BytesIO(raw))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        img = _enhance_for_ocr(img)

        quality = 90
        for scale in [1.0, 0.75, 0.5, 0.35, 0.25]:
            w, h = int(img.width * scale), int(img.height * scale)
            resized = img.resize((w, h), Image.LANCZOS) if scale < 1.0 else img
            buf = io.BytesIO()
            resized.save(buf, format="JPEG", quality=quality, optimize=True)
            data = buf.getvalue()
            if len(data) <= MAX_IMAGE_BYTES:
                return base64.b64encode(data).decode("utf-8"), "image/jpeg"
            quality = max(quality - 10, 50)

        resized = img.resize((int(img.width * 0.2), int(img.height * 0.2)), Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format="JPEG", quality=50)
        data = buf.getvalue()
        return base64.b64encode(data).decode("utf-8"), "image/jpeg"
    else:
        # Simple path: send raw bytes (no PIL available)
        if len(raw) > MAX_IMAGE_BYTES:
            logger.warning(f"Image {filepath} is {len(raw)} bytes, exceeds limit but no PIL to resize")
        return base64.b64encode(raw).decode("utf-8"), mime_type

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
- crew (crew identifier e.g. A, B, C, D)

## Manning / Crew Section
Production reports have a "Manning" section — usually a column on the RIGHT side of the form header. It lists the crew on the panel for that shift, GROUPED BY ROLE.

The layout is typically:
```
Manning
  Op.    Peter
         Wayne
         Clayton
         Turi
         Beau
  Elec.  Jackson
         Matt
  Mech.  Josh
         Tommy
```

The role label (Op., Elec., Mech.) appears ONCE, and all names listed below it until the next role label belong to that role. Each line is a SEPARATE person — never merge two names on separate lines into one.

CRITICAL: "Jackson" and "Matt" on separate lines means TWO electricians, not one person called "Jackson Matt".

Extract manning as:
- manning: array of objects, each with {"name": "first name or full name", "role": "operator|electrician|mechanic|deputy"}
  Example: [{"name": "Peter", "role": "operator"}, {"name": "Wayne", "role": "operator"}, {"name": "Jackson", "role": "electrician"}]
- manning_summary: object with counts per role
  Example: {"operators": 5, "electricians": 2, "mechanics": 2, "total": 9}

## Other Domain Knowledge
For gas readings at multiple locations, use arrays of objects. For tables (like production delays), use arrays of objects.

Common role abbreviations on forms:
- Op/Ops = Operator(s) — coal mine workers operating equipment
- Elec = Electrician(s)
- Mech = Mechanical trades / Fitter(s)
- Dep = Deputy (statutory inspection officer)
- UM = Undermanager
- SSM/SSE = Site Senior Manager / Site Senior Executive
- ERZ = Explosion Risk Zone controller
- CO = Control Room Operator
- DO = Development Operator

Common mine abbreviations:
- MG = Maingate, TG = Tailgate, CT = Cut-through
- SOP = Standard Operating Procedure
- TARP = Trigger Action Response Plan
- SCARIN = Strata Control and Reinforcement Inspection
- PUR = Powered Unrestricted Roof support
- MCT = Mean Cycle Time, TTPC = Time To Pick Change, TTLC = Time To Lace Change
- SOS = Start Of Shift, EOS = End Of Shift
- DS = Day Shift, AS = Afternoon Shift, NS = Night Shift
- AFC = Armoured Face Conveyor, BSL = Beam Stage Loader
- RD = Road Development, CT = Cut-through
- VFL = Visible Felt Leadership, SLAMs = Stop Look Assess Manage
- C/T = Cycle Time or Cut-through (context dependent)

Read handwriting carefully. If a value is illegible, set it to null. Don't guess.

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
