"""dd-extract CLI: extract text from PDFs."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from dd_extract.pdf import PDFExtractor


@click.command()
@click.argument("source")
@click.option(
    "--engine",
    type=click.Choice(["pypdf", "docling"]),
    default="pypdf",
    show_default=True,
    help="Extraction engine.",
)
@click.option(
    "--max-chars",
    default=12_000,
    type=int,
    show_default=True,
    help="Truncate output to N characters.",
)
@click.option(
    "--out",
    default="",
    help="Output file (default: stdout).",
)
def main(source: str, engine: str, max_chars: int, out: str) -> None:
    """Extract text from a PDF file or URL.

    SOURCE is a local file path or an http(s) URL to a PDF.

    \b
    Examples:
      dd-extract paper.pdf
      dd-extract paper.pdf --engine docling --max-chars 24000
      dd-extract https://arxiv.org/pdf/2312.12345 --out paper.md
      dd-extract paper.pdf --out paper.md
    """
    extractor = PDFExtractor(engine=engine, max_chars=max_chars)

    if source.startswith("http://") or source.startswith("https://"):
        click.echo(f"Downloading {source} ...", err=True)
        text = extractor.from_url(source)
    else:
        path = Path(source)
        if not path.exists():
            click.echo(f"Error: file not found: {source}", err=True)
            sys.exit(1)
        text = extractor.from_file(path)

    click.echo(f"Extracted {len(text):,} characters ({engine})", err=True)

    if out:
        Path(out).write_text(text, encoding="utf-8")
        click.echo(f"Written to {out}", err=True)
    else:
        click.echo(text)


if __name__ == "__main__":
    main()
