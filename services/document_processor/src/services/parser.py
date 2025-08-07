from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import TableItem, PictureItem, DocItem
from docling.chunking import HybridChunker
from docling_core.transforms.chunker import DocChunk

from PIL.Image import Image
from typing import List, Literal, Dict, Any
from dataclasses import dataclass
import io
import base64
from pathlib import Path

ChunkType = Literal["text", "table", "image"]

@dataclass
class DocumentChunk:
    content: str
    type: ChunkType
    source_page: int
    metadata: Dict[str, Any]

class PdfParser:
    def __init__(self, chunk_size: int = 256, image_resolution_scale: float = 2.0):
        pipeline_options = PdfPipelineOptions(
            images_scale=image_resolution_scale,
            generate_page_images=True,
            generate_picture_images=True
        )
        self.converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )
        self.chunker = HybridChunker(max_tokens_per_chunk=chunk_size)

    def _image_to_base64(self, image: Image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def parse(self, file_path: Path) -> List[DocumentChunk]:
        doc: DocItem = self.converter.convert(str(file_path)).document
        text_chunks = list(self.chunker.chunk(doc))
        visual_items = [item for item, _ in doc.iterate_items() if isinstance(item, (TableItem, PictureItem))]
        all_items = text_chunks + visual_items

        chunks: List[DocumentChunk] = []

        for item in all_items:
            try:
                if isinstance(item, DocChunk):
                    if item.text and item.text.strip():
                        page = item.meta.doc_items[0].prov[0].page_no if item.meta and item.meta.doc_items else 0
                        chunks.append(DocumentChunk(content=item.text, type="text", source_page=page, metadata={}))
                elif isinstance(item, TableItem):
                    image_b64 = self._image_to_base64(item.get_image(doc))
                    caption = item.caption_text(doc)
                    page = item.prov[0].page_no if item.prov else 0
                    chunks.append(DocumentChunk(content=image_b64, type="table", source_page=page, metadata={"caption": caption}))
                elif isinstance(item, PictureItem):
                    image_b64 = self._image_to_base64(item.get_image(doc))
                    caption = item.caption_text(doc)
                    page = item.prov[0].page_no if item.prov else 0
                    chunks.append(DocumentChunk(content=image_b64, type="image", source_page=page, metadata={"caption": caption}))
            except Exception as e:
                print(f"Error procesando elemento: {e}")
        return chunks