"""Basic tests for PDFExtractor."""

import pytest
from dd_extract.pdf import PDFExtractor


def test_init_defaults():
    ext = PDFExtractor()
    assert ext.engine == "pypdf"
    assert ext.max_chars == 12_000


def test_init_docling():
    ext = PDFExtractor(engine="docling", max_chars=5000)
    assert ext.engine == "docling"
    assert ext.max_chars == 5000


def test_invalid_engine():
    with pytest.raises(ValueError, match="Unknown engine"):
        PDFExtractor(engine="invalid")


def test_repr():
    ext = PDFExtractor(engine="pypdf", max_chars=8000)
    assert repr(ext) == "PDFExtractor(engine='pypdf', max_chars=8000)"
