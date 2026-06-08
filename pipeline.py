from pathlib import Path

DOCUMENTS_DIR = Path(__file__).parent / "documents"


def _source_type(filename: str) -> str:
    if "reddit" in filename:
        return "reddit"
    if "google_maps" in filename:
        return "google_maps"
    return "web"


def load_documents() -> list[dict]:
    """Load all .txt files from /documents.

    Returns a list of dicts, each with:
      id          – filename stem (unique, used as ChromaDB document id prefix)
      text        – cleaned document text
      source      – filename (surfaced in metadata for attribution)
      source_type – "reddit" | "google_maps" | "web"
    """
    docs = []
    for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        # Collapse runs of 3+ blank lines down to 2 so paragraph boundaries stay
        # intact without creating empty chunks later.
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        docs.append(
            {
                "id": path.stem,
                "text": text,
                "source": path.name,
                "source_type": _source_type(path.name),
            }
        )
    return docs


def chunk_document(doc: dict) -> list[dict]:
    """Split one document into paragraph-aligned chunks.

    Each blank-line-separated paragraph (one Reddit comment or one Google Maps
    review) becomes its own chunk, preserving natural semantic boundaries.

    Returns a list of dicts, each with:
      id          – "{doc_id}_chunk_{n}" (unique across the collection)
      text        – chunk text ready for embedding
      source      – propagated from the parent document
      source_type – propagated from the parent document
      chunk_index – 0-based position within this document
    """
    paragraphs = [p.strip() for p in doc["text"].split("\n\n") if p.strip()]
    return [
        {
            "id": f"{doc['id']}_chunk_{i}",
            "text": para,
            "source": doc["source"],
            "source_type": doc["source_type"],
            "chunk_index": i,
        }
        for i, para in enumerate(paragraphs)
    ]
