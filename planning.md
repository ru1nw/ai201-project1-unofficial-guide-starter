# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

**Good spots to study around Georgia Tech campus.**

Students usually have their own quiet spots that are not well known, and the well known places are always so packed that students develop strategies to combat that. Study places are also not well documented since most buildings have nooks of tables and chairs that aren't advertised.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | what are the best study spots at georgia tech? : r/gatech | best on-campus study spots | https://www.reddit.com/r/gatech/comments/1n7r08d |
| 2 | what are the best study spots around campus? : r/gatech | best on-campus study spots | https://www.reddit.com/r/gatech/comments/19eltzk |
| 3 | Best place to study on campus? : r/gatech | best on-campus study spots | https://www.reddit.com/r/gatech/comments/xpktnk |
| 4 | Any study spots with standing desks on campus? : r/gatech | on-campus study spots with standing desks | https://www.reddit.com/r/gatech/comments/sp7civ |
| 5 | Quietest place to study on campus? : r/gatech | quiet on-campus spots | https://www.reddit.com/r/gatech/comments/160e12g |
| 6 | Quiet places to take a midterm on campus tonight : r/gatech | quiet on-campus spots | https://www.reddit.com/r/gatech/comments/1140r0b |
| 7 | Any Good Libraries or Quiet Place to study? : r/gatech | quiet on-campus spots | https://www.reddit.com/r/gatech/comments/u8ro4u |
| 8 | Classroom Building Access After Hours : r/gatech | after-hours building access | https://www.reddit.com/r/gatech/comments/125tj64 |
| 9 | good places to study off-campus in tech square? : r/gatech | off-campus study spots | https://www.reddit.com/r/gatech/comments/nhf3c2 |
| 10 | StudyHive: Your Guide to Study Spots On-and-Off Campus! – Student Government Association | on- and off-campus study spots | https://www.sga.gatech.edu/studyhive-a-guide-to-study-spots-on-and-off-campus/ |
| 11 | Google Maps | reviews for Klaus | https://maps.app.goo.gl/cT5JGKzFWENGkT7U9 |
| 12 | Google Maps | reviews for library | https://maps.app.goo.gl/8qZziapxAQHd5kHu9 |
| 13 | Google Maps | reviews for Crosland Tower | https://maps.app.goo.gl/WLJZPrxu64HiiYZ79 |
| 14 | Google Maps | reviews for Price Gilbert | https://maps.app.goo.gl/eFjXr8g7WX3SxZXo7 |
| 15 | Google Maps | reviews for student center | https://maps.app.goo.gl/qqWTUbSK1KP7FTeKA |
| 16 | Google Maps | reviews for Clough (CULC) | https://maps.app.goo.gl/7QLHJqTMNs1EUepf9 |
| 17 | Google Maps | reviews for Kendeda | https://maps.app.goo.gl/Dfc8FQ9CBGoWUGCaA |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 256 tokens

**Overlap:** 50 tokens

**Reasoning:** Reddit comments and Google Maps reviews are usually only a few sentences long, so short tokens is enough to cover most comments/reviews. Tokens too long might get mixed up with other comments and will introduce unnecessary contexts.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2

**Top-k:** k=5

**Production tradeoff reflection:**

The current approach prioritizes speed and cost efficiency over maximum retrieval quality. The main risk is missing nuanced context in informal language.

Upgrading the embedding model to all-mpnet-base-v2 or nomic-embed-text-v1 (768 dimensions) to improve retrieval precision on domain-specific language. Reddit and review text use informal vernacular, slang, and product-specific terminology that smaller models may miss. A larger model would reduce false positives (retrieving tangentially related chunks) and improve ranking of truly relevant content.

Increasing k to 7–10 if retrieval latency isn't critical, to provide more context diversity to the LLM. This helps when synthesizing summaries across multiple reviews or when a single chunk lacks sufficient detail.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Who can enter CODA? | Graduate/PhD students and students who have review session/office hours there. |
| 2 | What are the quiet floors in Croland Tower? | 6th and 7th floor. |
| 3 | What do students say about Klaus? | It's usually quiet with hidden study spots. |
| 4 | Tell me about reserving rooms. | Rooms in Crosland, Price Gilbert library, and CULC can be reserved for a couple hours. However, they can also be accessed when it's not reserved. |
| 5 | Is student center noisy? | Yes, stay away if you want a quiet place to study, especially during mid-day. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Some joke Reddit comments might make their way into the answers.

2. Some longer comments/reviews might get chunked off.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
[Ingestion] plain text files in /documents copied from websites
     ↓
[Chunking] Python `str` methods
     ↓
[Embedding & Storage] sentence-transformers + chromadb
     ↓
[Retrieval] chromadb
     ↓
[Generation] Groq

```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

I'll give Claude my Chunking Strategy section and ask it to implement `chunk_text()` with my specified chunk size and overlap.

**Milestone 4 — Embedding and retrieval:**

I'll give Claude my Retrieval Approach section and ask it to embed chunks and implement store and retrieve using Chroma.

**Milestone 5 — Generation and interface:**

I'll ask Claude to implement `generate_response()` with Groq. I'll give Claude the desired interface and ask it to implement it with Gradio web UI.