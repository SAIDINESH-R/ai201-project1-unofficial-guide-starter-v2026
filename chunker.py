"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""
import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks




def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Splits each thread on reply boundaries instead of a fixed character count.

    Each document here is a Q&A thread: "THREAD: <question> --- reply N
    (votes) --- <text> --- reply N+1 (votes) --- <text> ...". A fixed 800-char
    window either merges unrelated replies together or cuts one in half. This
    strategy keeps each reply as its own chunk, with the thread's original
    question prepended so the chunk still makes sense read on its own.

    Replies under MIN_CHUNK_CHARS (100) get merged with the next reply instead
    of staying as an unusably short fragment — this is what criterion 4 checks.
    """
    MIN_CHUNK_CHARS = 100

    reply_pattern = re.compile(
        r"---\s*reply\s*(\d+)\s*\((\d+)\s*votes?\)\s*---", re.IGNORECASE
    )

    chunks: list[Chunk] = []

    for doc in documents:
        match_iter = list(reply_pattern.finditer(doc.text))

        if not match_iter:
            # No reply markers found — fall back to keeping the whole doc as one chunk
            text = doc.text.strip()
            if text:
                chunks.append(
                    Chunk(
                        text=text,
                        source=doc.source,
                        index=0,
                        produced_by="chunker.py::split_documents",
                    )
                )
            continue

        # Thread question is everything before the first reply marker
        thread_title = doc.text[: match_iter[0].start()].strip()

        # Build (vote_count, reply_text) pairs for each reply
        replies = []
        for i, m in enumerate(match_iter):
            votes = int(m.group(2))
            start = m.end()
            end = match_iter[i + 1].start() if i + 1 < len(match_iter) else len(doc.text)
            reply_text = doc.text[start:end].strip()
            replies.append((votes, reply_text))

        # Merge short replies forward into the next one
        merged: list[tuple[int, str]] = []
        buffer_votes, buffer_text = None, ""
        for votes, text in replies:
            if buffer_text:
                buffer_text = buffer_text + " " + text
                buffer_votes = max(buffer_votes, votes)
            else:
                buffer_votes, buffer_text = votes, text

            candidate = f"{thread_title}\n{buffer_text}"
            if len(candidate) >= MIN_CHUNK_CHARS:
                merged.append((buffer_votes, buffer_text))
                buffer_votes, buffer_text = None, ""

        if buffer_text:
            # Leftover short tail — merge into the last chunk instead of dropping it
            if merged:
                last_votes, last_text = merged[-1]
                merged[-1] = (max(last_votes, buffer_votes), last_text + " " + buffer_text)
            else:
                merged.append((buffer_votes, buffer_text))

        for i, (votes, text) in enumerate(merged):
            chunk_text = f"{thread_title}\n{text}"
            chunks.append(
                Chunk(
                    text=chunk_text,
                    source=doc.source,
                    index=i,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
