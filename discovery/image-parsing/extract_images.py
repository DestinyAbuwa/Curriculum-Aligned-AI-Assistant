"""Extract usable figures from the sample course PDFs with Docling.

Writes PNGs to discovery/image-parsing/images/<doc>/p<page>_<n>.png and a
discovery/image-parsing/images.json list of ImageRecord dicts.
"""

import json
from dataclasses import asdict
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DocItem, PictureItem, SectionHeaderItem, TitleItem

from curriculum_aligned_ai_assistant.image_index import ImageRecord, build_context, is_usable_size

REPO_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = REPO_ROOT / "discovery" / "chunking-methods" / "sample_pdfs"
OUT_DIR = REPO_ROOT / "discovery" / "image-parsing"
IMAGES_DIR = OUT_DIR / "images"


def _text_of(item: DocItem) -> str:
    if isinstance(item, PictureItem):
        return ""
    return str(getattr(item, "text", "")).strip()


def _page_of(item: DocItem) -> int | None:
    return item.prov[0].page_no if item.prov else None


def extract_pdf(converter: DocumentConverter, pdf: Path) -> tuple[int, list[ImageRecord]]:
    doc = converter.convert(pdf).document
    folder = pdf.stem.replace(" ", "_")[:40]
    items = [item for item, _level in doc.iterate_items() if isinstance(item, DocItem)]
    captions = {
        id(item): item.caption_text(doc).strip() for item in items if isinstance(item, PictureItem)
    }
    found = 0
    records: list[ImageRecord] = []
    heading = ""
    heading_page: int | None = None
    for index, item in enumerate(items):
        if isinstance(item, SectionHeaderItem | TitleItem):
            heading = item.text
            heading_page = _page_of(item)
        elif isinstance(item, PictureItem):
            n = found
            found += 1
            image = item.get_image(doc)
            if image is None or not is_usable_size(*image.size):
                continue
            page = item.prov[0].page_no
            # A caption that belongs to a different picture is not this picture's context.
            foreign = {c for key, c in captions.items() if key != id(item) and c}

            def nearby(
                others: list[DocItem], page: int = page, foreign: set[str] = foreign
            ) -> list[str]:
                return [
                    text
                    for other in others
                    if _page_of(other) == page and (text := _text_of(other)) and text not in foreign
                ]

            before = nearby(items[:index])
            after = nearby(items[index + 1 :])
            path = IMAGES_DIR / folder / f"p{page}_{n}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path)
            records.append(
                ImageRecord(
                    source=pdf.stem,
                    page=page,
                    heading=heading if heading_page == page else "",
                    caption=item.caption_text(doc),
                    file=path.relative_to(REPO_ROOT).as_posix(),
                    context=build_context(before, after),
                )
            )
    return found, records


def main() -> None:
    options = PdfPipelineOptions()
    options.do_ocr = False
    options.generate_picture_images = True
    options.images_scale = 2.0
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )
    all_records: list[ImageRecord] = []
    total_found = 0
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        found, records = extract_pdf(converter, pdf)
        print(f"{pdf.stem}: {found} pictures, {len(records)} kept", flush=True)
        total_found += found
        all_records.extend(records)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "images.json").write_text(
        json.dumps([asdict(r) for r in all_records], indent=2), encoding="utf-8"
    )
    print(f"Total: {total_found} pictures, {len(all_records)} kept")


if __name__ == "__main__":
    main()
