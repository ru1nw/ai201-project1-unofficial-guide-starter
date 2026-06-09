"""RAG pipeline for the Georgia Tech study spots unofficial guide.

Stages: document ingestion → chunking → embedding & storage → retrieval
→ generation.
"""

from os import getenv
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

CHROMA_PATH = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "study_spots"
DOCUMENTS_DIR = Path(__file__).parent / "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GROQ_API_KEY = getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"
TOP_K = 5

_ef = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=_ef,
)


def _source_type(filename: str) -> str:
    if "reddit" in filename:
        return "reddit"
    if "google_maps" in filename:
        return "google_maps"
    return "web"


def load_documents() -> list[dict]:
    """Load all .txt files from /documents.

    Returns a list of dicts, each with:
      id          --  filename stem (used as Chroma document id prefix)
      text        --  cleaned document text
      source      --  filename (surfaced in metadata for attribution)
      source_type --  "reddit" | "google_maps" | "web"
    """
    docs = []
    for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        # Collapse runs of 3+ blank lines down to 2 so paragraph
        # boundaries stay intact without creating empty chunks later.
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

    Each blank-line-separated paragraph (one Reddit comment or one
    Google Maps review) becomes its own chunk, preserving natural
    semantic boundaries.

    Returns a list of dicts, each with:
      id          --  "{doc_id}_chunk_{n}"
      text        --  chunk text ready for embedding
      source      --  propagated from the parent document
      source_type --  propagated from the parent document
      chunk_index --  0-based position within this document
    """
    paragraphs = [
        p.strip() for p in doc["text"].split("\n\n") if p.strip()
    ]

    # For Google Maps and Reddit documents the first paragraph is the
    # location name or post title. Prepend it to every subsequent chunk
    # so the embedding carries that context — otherwise isolated
    # reviews/comments drift away from queries that mention the location
    # or topic. The bare first paragraph is dropped since it has no
    # content of its own.
    if doc["source_type"] in ("google_maps", "reddit") and paragraphs:
        header = paragraphs[0]
        paragraphs = [f"{header}: {p}" for p in paragraphs[1:]]

    # SGA web document: each paragraph starts with a location name on
    # its own line. Reformat as "Location: content" so the location
    # label is explicitly attached to the chunk, consistent with the
    # google_maps prefix style.
    elif doc["source_type"] == "web":
        formatted = []
        for para in paragraphs:
            location, _, content = para.partition("\n")
            formatted.append(f"{location}: {content}" if content else para)
        paragraphs = formatted

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


def embed_and_store(chunks: list[dict]) -> chromadb.Collection:
    """Embed chunks and store them in a persistent Chroma collection.

    Uses upsert() so the function is safe to call multiple times -
    re-running the pipeline won't raise duplicate-ID errors.

    Returns the collection.
    """
    _collection.upsert(
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
    return _collection


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """Return the k most relevant chunks for a query.

    ChromaDB embeds the query with the same model used at index time,
    ranks by cosine similarity, and returns the top-k results.

    Each result dict contains:
      text        --  the chunk text, used as context for generation
      source      --  filename, for attribution in the response
      source_type --  "reddit" | "google_maps" | "web"
    """
    results = _collection.query(query_texts=[query], n_results=k)
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


_SYSTEM_PROMPT = """\
You are an assistant that helps Georgia Tech students find study spots.

Answer ONLY using the context passages provided in the user message. \
Do not draw on outside knowledge and do not speculate.
Every claim must cite its source filename in brackets, e.g. \
"According to [1-reddit-1n7r08d.txt], ..." or \
"A review in [13-google_maps-crosland.txt] says ...".
When multiple sources support the same point, cite each one.
If the context does not contain enough information to answer the \
question, say exactly: \
"I don't have information about that in my sources."\
"""


def generate_response(query: str, chunks: list[dict]) -> str:
    """Generate a grounded answer to query using the provided chunks.

    Sends the chunks as labelled context passages to Groq and instructs
    the model to cite filenames and refuse to answer beyond what they
    contain.
    """
    context = "\n\n".join(
        f"[{c['source']}]\n\"{c['text']}\""
        for c in chunks
    )
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": _SYSTEM_PROMPT
            },{
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            },
        ],
    )
    return response.choices[0].message.content


def _init_collection():
    chunks = [c for d in load_documents() for c in chunk_document(d)]
    embed_and_store(chunks)
    print(f"Ingestion complete. {len(chunks)} chunks stored.")


def ask(question: str) -> dict:
    """End-to-end pipeline.

    Retrieves relevant chunks then generate a grounded answer. If the
    collection is not initiated, initiate it.

    Returns:
      answer  --  the LLM response with inline source citations
      sources --  list of source filenames that were retrieved
    """
    if ((not isinstance(_collection, chromadb.Collection)) or
        (_collection.count() == 0)):
        print("initializing collection")
        _init_collection()
    chunks = retrieve(question)
    answer = generate_response(question, chunks)
    sources = [
        f"[{c['distance']:.4f}] ({c['source']}) {c['text']}" for c in chunks
    ]
    return {"answer": answer, "sources": sources}
