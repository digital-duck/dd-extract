"""PDF text extraction with pluggable engines.

Engines
-------
pypdf   — fast, lightweight, text-only; best for single-column PDFs.
docling — IBM layout-aware engine; preserves tables, figures, multi-column
          reading order.  Requires ``pip install dd-extract[docling]``.
"""

from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

import httpx


class PDFExtractor:
    """Extract text/markdown from PDFs.

    Parameters
    ----------
    engine : str
        ``'pypdf'`` (default) or ``'docling'``.
    max_chars : int
        Truncate output to this many characters (default 12 000).

    Examples
    --------
    >>> ext = PDFExtractor()
    >>> text = ext.from_file("paper.pdf")

    >>> ext = PDFExtractor(engine="docling", max_chars=24_000)
    >>> text = ext.from_url("https://arxiv.org/pdf/2312.12345")
    """

    ENGINES = ("pypdf", "docling")

    def __init__(self, engine: str = "pypdf", max_chars: int = 12_000):
        if engine not in self.ENGINES:
            raise ValueError(
                f"Unknown engine: {engine!r}  (choose from {self.ENGINES})"
            )
        self.engine = engine
        self.max_chars = max_chars

    def from_bytes(self, data: bytes) -> str:
        """Extract text from raw PDF bytes."""
        if self.engine == "docling":
            return self._docling(data)
        return self._pypdf(data)

    def from_file(self, path: str | Path) -> str:
        """Extract text from a local PDF file."""
        return self.from_bytes(Path(path).read_bytes())

    def from_url(self, url: str, timeout: float = 30.0) -> str:
        """Download a PDF from *url* and extract text."""
        resp = httpx.get(url, timeout=timeout, follow_redirects=True)
        resp.raise_for_status()
        return self.from_bytes(resp.content)

    # -- engines ----------------------------------------------------------

    def _pypdf(self, data: bytes) -> str:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(io.BytesIO(data))
        parts: list[str] = []
        total = 0
        for page in reader.pages:
            text = page.extract_text() or ""
            parts.append(text)
            total += len(text)
            if total >= self.max_chars:
                break
        return "\n".join(parts)[: self.max_chars]

    def _docling(self, data: bytes) -> str:
        try:
            from docling.document_converter import DocumentConverter  # type: ignore
        except ImportError:
            # Graceful fallback to pypdf
            return self._pypdf(data)

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
                fh.write(data)
                tmp_path = fh.name
            converter = DocumentConverter()
            result = converter.convert(tmp_path)
            md = result.document.export_to_markdown()
            return md[: self.max_chars]
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def __repr__(self) -> str:
        return f"PDFExtractor(engine={self.engine!r}, max_chars={self.max_chars})"
