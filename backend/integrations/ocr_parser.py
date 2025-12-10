"""
OCR Parser
- Supports OCR for scanned PDFs and image files.
- Returns page/loc-wise extracted text for citations and chunking.

Dependencies:
- Pillow (PIL)
- pytesseract (Python wrapper)
Optional (recommended):
- PyMuPDF (fitz) for PDF -> image rendering (best for servers)
Alternative:
- pdf2image (requires poppler system install)

Note:
- You must install the Tesseract OCR engine on your OS for pytesseract to work.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import os
import re
import importlib
import logging

logger = logging.getLogger(__name__)


class OCRUnavailableError(RuntimeError):
    """Raised when OCR cannot run due to missing dependencies/binaries."""


class OCRError(RuntimeError):
    """Raised when OCR fails unexpectedly."""


@dataclass
class OCRConfig:
    # language(s) for OCR (e.g., "eng", "eng+hin")
    lang: str = "eng"

    # DPI for PDF rendering (higher = better accuracy, slower)
    dpi: int = 200

    # Page range for PDFs (1-indexed). None means all pages.
    start_page: Optional[int] = None
    end_page: Optional[int] = None

    # Preprocess image to improve OCR
    preprocess: bool = True

    # Tesseract config tuning
    psm: int = 3  # Page segmentation mode
    oem: int = 3  # OCR engine mode

    # Limit output size per page to avoid runaway text
    max_chars_per_page: int = 100_000

    # Strip excessive whitespace/newlines
    normalize_whitespace: bool = True

    # If True, suppress errors and return best-effort
    best_effort: bool = True


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _require_pytesseract():
    if not _has_module("pytesseract"):
        raise OCRUnavailableError(
            "pytesseract is not installed. Install it: pip install pytesseract"
        )
    import pytesseract  # noqa: F401

    # If tesseract binary is missing, pytesseract throws at runtime.
    # We'll detect by calling get_tesseract_version safely.
    try:
        import pytesseract

        _ = pytesseract.get_tesseract_version()
    except Exception as e:
        raise OCRUnavailableError(
            "Tesseract OCR engine not found on system PATH. "
            "Install tesseract-ocr (system package) and ensure 'tesseract' is available."
        ) from e


def _load_image_pil(path: str):
    if not _has_module("PIL"):
        raise OCRUnavailableError("Pillow is not installed. Install it: pip install pillow")
    from PIL import Image

    return Image.open(path)


def _preprocess_image(img):
    """Light preprocessing to improve OCR (grayscale + contrast + threshold)."""
    from PIL import ImageEnhance, ImageOps

    # Ensure RGB -> L
    img = img.convert("L")
    img = ImageOps.autocontrast(img)

    # Contrast boost
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    # Simple thresholding
    img = img.point(lambda p: 255 if p > 160 else 0)
    return img


def _normalize_text(text: str) -> str:
    # collapse too many blank lines and spaces
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _ocr_image(img, cfg: OCRConfig) -> str:
    _require_pytesseract()
    import pytesseract

    if cfg.preprocess:
        try:
            img = _preprocess_image(img)
        except Exception as e:
            logger.warning("OCR preprocess failed: %s", e)
            if not cfg.best_effort:
                raise

    tesseract_config = f"--oem {cfg.oem} --psm {cfg.psm}"
    try:
        text = pytesseract.image_to_string(img, lang=cfg.lang, config=tesseract_config)
    except Exception as e:
        raise OCRError(f"OCR failed: {e}") from e

    if cfg.normalize_whitespace:
        text = _normalize_text(text)

    if cfg.max_chars_per_page and len(text) > cfg.max_chars_per_page:
        text = text[: cfg.max_chars_per_page]

    return text


def _pdf_to_images_pymupdf(pdf_path: str, dpi: int, start: Optional[int], end: Optional[int]):
    """
    Render PDF pages to PIL images using PyMuPDF (fitz).
    start/end are 1-indexed.
    """
    if not _has_module("fitz"):
        raise OCRUnavailableError("PyMuPDF not installed (fitz). Install: pip install pymupdf")
    from PIL import Image
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count

    s = start if start is not None else 1
    e = end if end is not None else total_pages
    s = max(1, s)
    e = min(total_pages, e)

    zoom = dpi / 72.0  # PDF default 72dpi
    mat = fitz.Matrix(zoom, zoom)

    images = []
    for page_no in range(s, e + 1):
        page = doc.load_page(page_no - 1)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        images.append((page_no, img))

    return images


def _pdf_to_images_pdf2image(pdf_path: str, dpi: int, start: Optional[int], end: Optional[int]):
    """
    Render PDF pages to PIL images using pdf2image (requires poppler installed).
    start/end are 1-indexed.
    """
    if not _has_module("pdf2image"):
        raise OCRUnavailableError("pdf2image not installed. Install: pip install pdf2image")

    from pdf2image import convert_from_path

    # pdf2image uses first_page/last_page 1-indexed
    kwargs = {"dpi": dpi}
    if start is not None:
        kwargs["first_page"] = start
    if end is not None:
        kwargs["last_page"] = end

    try:
        imgs = convert_from_path(pdf_path, **kwargs)
    except Exception as e:
        raise OCRUnavailableError(
            "pdf2image failed. Make sure Poppler is installed on your system."
        ) from e

    # If first_page specified, enumerate pages accordingly
    start_page = start if start is not None else 1
    return [(start_page + i, img) for i, img in enumerate(imgs)]


def extract_text_from_image_file(image_path: str, cfg: Optional[OCRConfig] = None) -> Dict[str, Any]:
    """
    OCR for a single image file. Returns:
      { "loc": 1, "text": "...", "source": "ocr", "path": image_path }
    """
    cfg = cfg or OCRConfig()
    img = _load_image_pil(image_path)
    text = _ocr_image(img, cfg)
    return {"loc": 1, "text": text, "source": "ocr", "path": image_path}


def extract_text_from_pdf_ocr(pdf_path: str, cfg: Optional[OCRConfig] = None) -> List[Dict[str, Any]]:
    """
    OCR for scanned PDF. Returns list of:
      { "loc": page_no, "text": "...", "source": "ocr", "path": pdf_path }
    """
    cfg = cfg or OCRConfig()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)

    # Prefer PyMuPDF. Fallback to pdf2image.
    images: List[Tuple[int, Any]] = []
    errors: List[str] = []

    try:
        images = _pdf_to_images_pymupdf(pdf_path, cfg.dpi, cfg.start_page, cfg.end_page)
    except Exception as e:
        errors.append(f"PyMuPDF: {e}")

    if not images:
        try:
            images = _pdf_to_images_pdf2image(pdf_path, cfg.dpi, cfg.start_page, cfg.end_page)
        except Exception as e:
            errors.append(f"pdf2image: {e}")

    if not images:
        raise OCRUnavailableError(
            "Unable to render PDF to images for OCR. Tried PyMuPDF and pdf2image.\n"
            + "\n".join(errors)
        )

    out: List[Dict[str, Any]] = []
    for page_no, img in images:
        try:
            text = _ocr_image(img, cfg)
        except Exception as e:
            if cfg.best_effort:
                logger.warning("OCR failed on page %s: %s", page_no, e)
                text = ""
            else:
                raise
        out.append({"loc": page_no, "text": text, "source": "ocr", "path": pdf_path})

    return out


def extract_text_any(path: str, cfg: Optional[OCRConfig] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Convenience function:
    - If path is PDF -> returns list[page-wise]
    - Else -> returns dict for single image

    Use this in ingest_service when normal text extraction fails.
    """
    cfg = cfg or OCRConfig()
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf_ocr(path, cfg)
    else:
        return extract_text_from_image_file(path, cfg)
