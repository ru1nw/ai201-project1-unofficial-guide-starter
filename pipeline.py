from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

DOCUMENTS_DIR = Path(__file__).parent / "documents"
CHROMA_PATH = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "study_spots"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5


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

    # For Google Maps and Reddit documents the first paragraph is the location
    # name or post title. Prepend it to every subsequent chunk so the embedding
    # carries that context — otherwise isolated reviews/comments drift away from
    # queries that mention the location or topic. The bare first paragraph is
    # dropped since it has no content of its own.
    if doc["source_type"] in ("google_maps", "reddit") and paragraphs:
        header = paragraphs[0]
        paragraphs = [f"{header}: {p}" for p in paragraphs[1:]]

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


def embed_and_store(
    chunks: list[dict],
    collection_name: str = COLLECTION_NAME,
) -> chromadb.Collection:
    """Embed chunks with all-MiniLM-L6-v2 and store them in a persistent ChromaDB collection.

    Uses upsert() so the function is safe to call multiple times — re-running
    the pipeline won't raise duplicate-ID errors.

    Returns the collection, ready to pass directly to retrieve().
    """
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
    )
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[
            {
                "source": c["source"],
                "source_type": c["source_type"],
                "chunk_index": c["chunk_index"],
            }
            for c in chunks
        ],
    )
    return collection


def retrieve(
    query: str,
    collection: chromadb.Collection,
    k: int = TOP_K,
) -> list[dict]:
    """Return the k most relevant chunks for a query.

    ChromaDB embeds the query with the same model used at index time, ranks by
    cosine similarity, and returns the top-k results.

    Each result dict contains:
      text        – the chunk text, used as context for generation
      source      – filename, for attribution in the response
      source_type – "reddit" | "google_maps" | "web"
    """
    results = collection.query(query_texts=[query], n_results=k)
    return [
        {
            "text": doc,
            "source": meta["source"],
            "source_type": meta["source_type"],
            "distance": dist,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]
