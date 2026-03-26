import os
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.document import Document
from backend.models.document_category import DocumentCategory
from backend.services.ocr_service import classify_and_extract
from backend.services.document_manager import manage_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_documents(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Upload one or more scanned mine reports. Claude classifies and extracts each one."""
    results = []

    for file in files:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".pdf", ".tiff", ".tif", ".webp"):
            results.append({"filename": file.filename, "status": "error", "error": "Unsupported file type"})
            continue

        os.makedirs(settings.upload_dir, exist_ok=True)
        file_id = uuid.uuid4().hex[:12]
        saved_name = f"{file_id}{ext}"
        filepath = os.path.join(settings.upload_dir, saved_name)

        contents = await file.read()
        with open(filepath, "wb") as f:
            f.write(contents)

        doc = Document(
            filename=file.filename or saved_name,
            filepath=filepath,
            file_type=ext.lstrip("."),
            status="processing",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        try:
            # Step 1: OCR extraction
            result = await classify_and_extract(filepath)
            raw_fields = result.get("fields", {})
            raw_category = result.get("report_category", "unknown")

            # Step 2: Document management agent — classify, normalize, validate
            existing_cats = [
                {
                    "name": c.name,
                    "label": c.label,
                    "description": c.description,
                    "field_schema": c.field_schema,
                    "sample_count": c.sample_count,
                }
                for c in db.query(DocumentCategory).all()
            ]

            managed = await manage_document(raw_category, raw_fields, existing_cats)

            # Step 3: Create or update category
            cat_info = managed.get("category", {})
            cat_name = cat_info.get("name", raw_category)
            existing_cat = db.query(DocumentCategory).filter(DocumentCategory.name == cat_name).first()

            if existing_cat:
                existing_cat.sample_count += 1
            else:
                new_cat = DocumentCategory(
                    name=cat_name,
                    label=cat_info.get("label", cat_name),
                    description=cat_info.get("description", ""),
                    field_schema=cat_info.get("field_schema", {}),
                    sample_count=1,
                )
                db.add(new_cat)

            # Step 4: Store normalized data
            normalized = managed.get("normalized_fields", raw_fields)
            validation = managed.get("validation", {})

            doc.report_category = cat_name
            doc.extracted_data = normalized
            doc.raw_text = result.get("raw_text", "")
            doc.confidence = result.get("confidence", 0.0)
            doc.report_date = _parse_date(normalized.get("report_date"))
            doc.shift = normalized.get("shift")
            doc.panel = normalized.get("panel")
            doc.submitted_by = normalized.get("submitted_by")
            doc.status = "processed"
            db.commit()

            results.append({
                "id": doc.id,
                "filename": doc.filename,
                "status": "processed",
                "report_category": cat_name,
                "report_category_label": cat_info.get("label", cat_name),
                "confidence": doc.confidence,
                "extracted_data": normalized,
                "report_date": str(doc.report_date) if doc.report_date else None,
                "shift": doc.shift,
                "panel": doc.panel,
                "submitted_by": doc.submitted_by,
                "validation": validation,
            })
        except Exception as e:
            logger.exception(f"Extraction failed for {file.filename}")
            doc.status = "error"
            db.commit()
            results.append({"filename": file.filename, "status": "error", "error": str(e)})

    return results


@router.put("/{document_id}")
def update_document(document_id: int, data: dict, db: Session = Depends(get_db)):
    """Update extracted data after human review."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    if "extracted_data" in data:
        doc.extracted_data = data["extracted_data"]
    if "report_category" in data:
        doc.report_category = data["report_category"]
    if "status" in data:
        doc.status = data["status"]

    # Re-extract common fields from updated data
    fields = doc.extracted_data or {}
    doc.report_date = _parse_date(fields.get("report_date"))
    doc.shift = fields.get("shift")
    doc.panel = fields.get("panel")
    doc.submitted_by = fields.get("submitted_by")

    db.commit()
    return {"id": doc.id, "status": doc.status}


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and its file."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    if doc.filepath and os.path.exists(doc.filepath):
        os.remove(doc.filepath)
    db.delete(doc)
    db.commit()
    return {"status": "deleted"}


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """List all document categories the system has learned."""
    cats = db.query(DocumentCategory).order_by(DocumentCategory.sample_count.desc()).all()
    return [
        {
            "name": c.name,
            "label": c.label,
            "description": c.description,
            "field_schema": c.field_schema,
            "sample_count": c.sample_count,
        }
        for c in cats
    ]


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).limit(100).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "report_category": d.report_category,
            "report_date": str(d.report_date) if d.report_date else None,
            "shift": d.shift,
            "panel": d.panel,
            "submitted_by": d.submitted_by,
            "confidence": d.confidence,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]


@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return {
        "id": doc.id,
        "filename": doc.filename,
        "filepath": doc.filepath,
        "file_type": doc.file_type,
        "report_category": doc.report_category,
        "report_date": str(doc.report_date) if doc.report_date else None,
        "shift": doc.shift,
        "panel": doc.panel,
        "submitted_by": doc.submitted_by,
        "extracted_data": doc.extracted_data,
        "raw_text": doc.raw_text,
        "confidence": doc.confidence,
        "status": doc.status,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }


@router.get("/{document_id}/file")
def get_document_file(document_id: int, db: Session = Depends(get_db)):
    """Serve the original uploaded file."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    if not os.path.exists(doc.filepath):
        raise HTTPException(404, "File not found on disk")

    media_types = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "png": "image/png", "webp": "image/webp",
        "pdf": "application/pdf", "tiff": "image/tiff", "tif": "image/tiff",
    }
    media_type = media_types.get(doc.file_type or "", "application/octet-stream")
    return FileResponse(doc.filepath, media_type=media_type, filename=doc.filename)


def _parse_date(val):
    if not val:
        return None
    from datetime import datetime
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(val), fmt).date()
        except ValueError:
            continue
    return None
