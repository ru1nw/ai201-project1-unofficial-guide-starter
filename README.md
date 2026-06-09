# The Unofficial Guide — Project 1

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

**Good spots to study around Georgia Tech campus.**

Students usually have their own quiet spots that are not well known, and the well known places are always so packed that students develop strategies to combat that. Study places are also not well documented since most buildings have nooks of tables and chairs that aren't advertised.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | what are the best study spots at georgia tech? : r/gatech | Reddit thread | https://redd.it/1n7r08d |
| 2 | what are the best study spots around campus? : r/gatech | Reddit thread | https://redd.it/19eltzk |
| 3 | Best place to study on campus? : r/gatech | Reddit thread | https://redd.it/xpktnk |
| 4 | Any study spots with standing desks on campus? : r/gatech | Reddit thread | https://redd.it/sp7civ |
| 5 | Quietest place to study on campus? : r/gatech | Reddit thread | https://redd.it/160e12g |
| 6 | Quiet places to take a midterm on campus tonight : r/gatech | Reddit thread | https://redd.it/1140r0b |
| 7 | Any Good Libraries or Quiet Place to study? : r/gatech | Reddit thread | https://redd.it/u8ro4u |
| 8 | Classroom Building Access After Hours : r/gatech | Reddit thread | https://redd.it/125tj64 |
| 9 | good places to study off-campus in tech square? : r/gatech | Reddit thread | https://redd.it/nhf3c2 |
| 10 | StudyHive: Your Guide to Study Spots On-and-Off Campus! – Student Government Association | blog/review post | https://www.sga.gatech.edu/studyhive-a-guide-to-study-spots-on-and-off-campus/ |
| 11 | Klaus Advanced Computing Building - Google Maps | Google Maps reviews | https://maps.app.goo.gl/cT5JGKzFWENGkT7U9 |
| 12 | Georgia Tech Library - Google Maps | Google Maps reviews | https://maps.app.goo.gl/8qZziapxAQHd5kHu9 |
| 13 | Crosland Tower - Google Maps | Google Maps reviews | https://maps.app.goo.gl/WLJZPrxu64HiiYZ79 |
| 14 | Price Gilbert Memorial Library - Google Maps | Google Maps reviews | https://maps.app.goo.gl/eFjXr8g7WX3SxZXo7 |
| 15 | John Lewis Student Center - Google Maps | Google Maps reviews | https://maps.app.goo.gl/qqWTUbSK1KP7FTeKA |
| 16 | Clough Undergraduate Learning Commons - Google Maps | Google Maps reviews | https://maps.app.goo.gl/7QLHJqTMNs1EUepf9 |
| 17 | Kendeda Building - Google Maps | Google Maps reviews | https://maps.app.goo.gl/Dfc8FQ9CBGoWUGCaA |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 1 paragraph

**Overlap:** 0

**Why these choices fit your documents:** The documents are cleaned so only actual thread title, comments, and reviews are left, which are grouped together in a paragraph, and the commenters, unrelated descriptions, etc. are all removed. Since individual comments or reviews are left by completely different people, chunking by characters or tokens would mix completely different answers in a chunk, and overlapping would potentially make it worse. This makes chunking by paragraph the ideal choice.

**Final chunk count:** 303 chunks

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2

**Production tradeoff reflection:**

The current approach prioritizes speed and cost efficiency over maximum retrieval quality. The main risk is missing nuanced context in informal language.

Upgrading the embedding model to all-mpnet-base-v2 or nomic-embed-text-v1 (768 dimensions) to improve retrieval precision on domain-specific language. Reddit and review text use informal vernacular, slang, and product-specific terminology that smaller models may miss. A larger model would reduce false positives (retrieving tangentially related chunks) and improve ranking of truly relevant content.

Increasing k to 7–10 if retrieval latency isn't critical, to provide more context diversity to the LLM. This helps when synthesizing summaries across multiple reviews or when a single chunk lacks sufficient detail.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

```
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
```

**How source attribution is surfaced in the response:**

I asked it to cite the source filename within its response. I didn't specifically filter out any retrieved chunks because the model seems to be good enough to filter them out on its own, so the "sources" block in the final interface still lists the retrieved chunks.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Who can enter CODA? | Graduate/PhD students and students who have review session/office hours there. | most floors in CODA are only open to graduate and PhD students ...  entry may be restricted ... There is no information in the provided context about who else can enter CODA. | Relevant | Partially accurate (did not mention students with review session and office hours) |
| 2 | What are the quiet floors in Crosland? | 6th and 7th floor. | the quiet floors in Crosland ... are floor 6 and floor 7 | Relevant | Accurate |
| 3 | What do students say about study spots in Klaus? | It's usually quiet with hidden study spots. | usually quiet with some tucked-away study spots ... good spots with comfy chairs and fast WiFi ... a student [...] recommends the hallway on the 3rd floor connecting the Research and Classroom wings of Klaus as a quiet place to study | Relevant | Accurate |
| 4 | Tell me about reserving rooms. | Rooms in Crosland, Price Gilbert library, and CULC can be reserved for a couple hours. However, they can also be accessed when it's not reserved. | there is an issue with getting kicked out of a room for not reserving it, even if nobody has reserved the room ... A post ... mentions booking a meeting room as an option ... if you need a room in the library after hours, you can probably just use it without a reservation | Partially relevant | Partially accurate (Did not mention where the reservable rooms are other than in the library) |
| 5 | Is student center noisy? | Yes, stay away if you want a quiet place to study, especially during mid-day. | Student Center is "crowded and noisy" | Relevant | Accurate |

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

```What are some outdoor study spots?```

**What the system returned:**

```I don't have information about that in my sources.```

**Root cause (tied to a specific pipeline stage):** The model could not figure out more subtle notions that relates to outdoor such as "outside of (building)" or "rooftop". Some of the paragraphs are also really long where embedding does not perform as well.

**What you would change to fix it:** Use recursive chunking so longer paragraphs are split into sentences. Use a model with a higher dimensions to capture more semantics.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** The evaluation plan helped me figure out the general direction of what I want the final product to do. This comes in handy when I was deciding how to clean the sources and chunk them.

**One way your implementation diverged from the spec, and why:** I was originally chunking with token sizes, but after having some trouble with chunking size being too small in some cases and too large in others, I was reminded that I could use recursive chunking.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*

  ```
  read "Retrieval Approach" and "Architecture" sections in `planning.md`, then plan how you will implement the "Retrieval" step using chroma: implement `retrieve()` that finds the most relevant rule chunks for a question from chroma collection
  ```

- *What it produced:*

  ```
  retrieve(query, collection, k=5)

  - Call collection.query(query_texts=[query], n_results=k) — ChromaDB embeds the query with the same model, does the similarity search, and returns ranked results
  - Return a flat list of dicts with text, source, source_type — everything the generation step needs for a grounded response
  ```

- *What I changed or overrode:* Instead of passing collection as a parameter, I make collection a global variable and use that instead since a lot of functions also use that.

**Instance 2**

- *What I gave the AI:*
  
  ```
  Build a query interface using skeleton code provided in `app.py`
  ```

- *What it produced:*
  
  ```
  _collection = None

  def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        docs = load_documents()
        chunks = [c for d in docs for c in chunk_document(d)]
        _collection = embed_and_store(chunks)
    return _collection

  def ask(question: str) -> dict:
    chunks = retrieve(question, _get_collection())
  ...
  ```

- *What I changed or overrode:* I initialized `_collection` to fetch the Chroma collection that is already on the disk, instead of having to recreate the collection each time the program starts up.
