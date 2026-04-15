import hashlib
import os
from collections import defaultdict
from utils.logging_config import get_logger

logger = get_logger(__name__)


def process_text_file(file_path: str) -> dict:
    """
    Process a plain text file without using docling.
    Returns the same structure as extract_relevant() for consistency.

    Args:
        file_path: Path to the .txt file

    Returns:
        dict with keys: id, filename, mimetype, chunks
    """
    import os
    from utils.hash_utils import hash_id

    # Read the file
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Compute hash
    file_hash = hash_id(file_path)
    filename = os.path.basename(file_path)

    # Split content into chunks of ~1000 characters to match typical docling chunk sizes
    # This ensures embeddings stay within reasonable token limits
    chunk_size = 1000
    chunks = []

    # Split by paragraphs first (double newline)
    paragraphs = content.split('\n\n')
    current_chunk = ""
    chunk_index = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph would exceed chunk size, save current chunk
        if len(current_chunk) + len(para) + 2 > chunk_size and current_chunk:
            chunks.append({
                "page": chunk_index + 1,  # Use chunk_index + 1 as "page" number
                "type": "text",
                "text": current_chunk.strip()
            })
            chunk_index += 1
            current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para

    # Add the last chunk if any
    if current_chunk.strip():
        chunks.append({
            "page": chunk_index + 1,
            "type": "text",
            "text": current_chunk.strip()
        })

    # If no chunks were created (empty file), create a single empty chunk
    if not chunks:
        chunks.append({
            "page": 1,
            "type": "text",
            "text": ""
        })

    return {
        "id": file_hash,
        "filename": filename,
        "mimetype": "text/plain",
        "chunks": chunks,
    }


def extract_with_hybrid_chunker(doc_dict: dict) -> dict:
    """
    Deserialize a DoclingDocument JSON dict (from docling-serve) and apply
    HybridChunker to produce semantically coherent chunks with section metadata.

    Requires the ``docling`` Python SDK (``pip install docling``).
    Only called when ``HYBRID_CHUNKER_ENABLED=true``.

    Returns the same schema as ``extract_relevant()`` for drop-in compatibility,
    with extra fields per chunk:
        section_title    : title of the nearest heading above this chunk (or None)
        parent_section   : title of the parent section (or None)
        chunk_index      : 0-based position within this document
        prev_chunk_index : index of the preceding chunk (or None)
        next_chunk_index : index of the following chunk (or None)
    """
    try:
        from docling.datamodel.document import DoclingDocument
        from docling.chunking import HybridChunker
    except ImportError as exc:
        logger.error(
            "docling SDK not installed — falling back to extract_relevant(). "
            "Run: pip install docling",
            error=str(exc),
        )
        return extract_relevant(doc_dict)

    try:
        doc = DoclingDocument.model_validate(doc_dict)
    except Exception as exc:
        logger.warning(
            "extract_with_hybrid_chunker: DoclingDocument validation failed, "
            "falling back to extract_relevant()",
            error=str(exc),
        )
        return extract_relevant(doc_dict)

    chunker = HybridChunker()
    try:
        raw_chunks = list(chunker.chunk(doc))
    except Exception as exc:
        logger.warning(
            "extract_with_hybrid_chunker: HybridChunker.chunk() failed, "
            "falling back to extract_relevant()",
            error=str(exc),
        )
        return extract_relevant(doc_dict)

    chunks = []
    total = len(raw_chunks)

    for i, chunk in enumerate(raw_chunks):
        # Contextualize enriches the chunk text with heading breadcrumbs
        try:
            ctx = chunker.contextualize(chunk)
            text = ctx.text
            headings = getattr(ctx.meta, "headings", None) or []
        except Exception:
            text = getattr(chunk, "text", "")
            headings = []

        # Extract page number from the first provenance entry (best-effort)
        page_no = None
        try:
            doc_items = getattr(chunk.meta, "doc_items", None) or []
            if doc_items:
                prov_list = getattr(doc_items[0], "prov", None) or []
                if prov_list:
                    page_no = getattr(prov_list[0], "page_no", None)
        except Exception:
            pass

        chunks.append({
            "page": page_no,
            "type": "text",
            "text": text,
            "section_title": headings[0] if len(headings) > 0 else None,
            "parent_section": headings[1] if len(headings) > 1 else None,
            "chunk_index": i,
            "prev_chunk_index": i - 1 if i > 0 else None,
            "next_chunk_index": i + 1 if i < total - 1 else None,
        })

    if not chunks:
        logger.warning(
            "extract_with_hybrid_chunker: no chunks produced, falling back to extract_relevant()"
        )
        return extract_relevant(doc_dict)

    origin = doc_dict.get("origin", {})
    return {
        "id": origin.get("binary_hash"),
        "filename": origin.get("filename"),
        "mimetype": origin.get("mimetype"),
        "chunks": chunks,
    }


def extract_relevant(doc_dict: dict) -> dict:
    """
    Given the full export_to_dict() result:
      - Grabs origin metadata (hash, filename, mimetype)
      - Finds every text fragment in `texts`, groups them by page_no
      - Flattens tables in `tables` into tab-separated text, grouping by row
      - Concatenates each page's fragments and each table into its own chunk
    Returns a slimmed dict ready for indexing, with each chunk under "text".
    """
    origin = doc_dict.get("origin", {})
    chunks = []

    # 1) process free-text fragments
    page_texts = defaultdict(list)
    for txt in doc_dict.get("texts", []):
        prov = txt.get("prov", [])
        page_no = prov[0].get("page_no") if prov else None
        if page_no is not None:
            page_texts[page_no].append(txt.get("text", "").strip())

    for page in sorted(page_texts):
        chunks.append(
            {"page": page, "type": "text", "text": "\n".join(page_texts[page])}
        )

    # 2) process tables
    for t_idx, table in enumerate(doc_dict.get("tables", [])):
        prov = table.get("prov", [])
        page_no = prov[0].get("page_no") if prov else None

        # group cells by their row index
        rows = defaultdict(list)
        for cell in table.get("data").get("table_cells", []):
            r = cell.get("start_row_offset_idx")
            c = cell.get("start_col_offset_idx")
            text = cell.get("text", "").strip()
            rows[r].append((c, text))

        # build a tab‑separated line for each row, in order
        flat_rows = []
        for r in sorted(rows):
            cells = [txt for _, txt in sorted(rows[r], key=lambda x: x[0])]
            flat_rows.append("\t".join(cells))

        chunks.append(
            {
                "page": page_no,
                "type": "table",
                "table_index": t_idx,
                "text": "\n".join(flat_rows),
            }
        )

    return {
        "id": origin.get("binary_hash"),
        "filename": origin.get("filename"),
        "mimetype": origin.get("mimetype"),
        "chunks": chunks,
    }
