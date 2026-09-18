"""
================================================================================
EXAMPLE 05: Document Loaders & Text Splitters (Chunking Strategies)
================================================================================
Before text can be embedded or retrieved in RAG, large documents must be split
into meaningful chunks.
Learn:
1. Why chunking matters (granularity vs context retention).
2. `RecursiveCharacterTextSplitter`: Splitting hierarchically by paragraphs,
   sentences, and words.
3. `chunk_size` and `chunk_overlap`: Preventing information loss at boundaries.
4. Managing `Document` objects with metadata.
================================================================================
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # Configures UTF-8 console and environment

from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter


SAMPLE_TECHNICAL_MANUAL = """
ACME CORP - AUTONOMOUS ROBOTICS SAFETY MANUAL (REV 4.2)

1. SYSTEM INITIALIZATION & SENSORS
Before engaging the hydraulic locomotion sub-system, all LiDAR optical arrays must be calibrated against the high-contrast checkerboard target at 3.0 meters distance. If the optical baseline reports greater than 0.05% error, the emergency halt relay (EHR-9) will automatically trip.

2. POWER MANAGEMENT & BATTERY SAFEGUARDS
The drone is powered by a dual lithium-sulfur power pack operating at 48V nominal. Operating temperatures must remain strictly between -10°C and +45°C. In the event of battery cell degradation exceeding 15% differential resistance, telemetry will broadcast Alert Code 882 ('Power Imbalance') to the regional ground station.

3. EMERGENCY DISENGAGEMENT PROTOCOLS
In an unrecoverable telemetry loss scenario lasting longer than 4500 milliseconds:
- The craft must immediately initiate automated hover stability.
- Descent rate will be throttled to precisely 0.8 meters per second.
- Acoustic hazard beacons must strobe at 4 Hz to alert personnel within a 20-meter radius.
- Do not attempt manual tether retrieval until beacon lights transition from red to solid amber.

4. ROUTINE MAINTENANCE & MOTOR LUBRICATION
Every 250 operating hours, technicians must replace the synthetic fluoropolymer seals on all four axial rotor bearings. Use exclusively ChemLube Synth-99 grease. Any standard petroleum-based lubricants will degrade the O-ring seals and invalidate the manufacturer warranty.
""".strip()


def demo_naive_vs_recursive_splitting():
    print("\n" + "=" * 60)
    print("PART 1: Comparing CharacterTextSplitter vs RecursiveCharacterTextSplitter")
    print("=" * 60)

    # 1. Naive character splitter (splits strictly on single separator, e.g. "\n\n")
    naive_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=300,
        chunk_overlap=50
    )
    naive_chunks = naive_splitter.split_text(SAMPLE_TECHNICAL_MANUAL)
    print(f"\n[Naive CharacterTextSplitter]: Produced {len(naive_chunks)} chunks.")

    # 2. Recursive splitter (splits on ["\n\n", "\n", " ", ""] intelligently)
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False
    )
    recursive_chunks = recursive_splitter.split_text(SAMPLE_TECHNICAL_MANUAL)
    print(f"[RecursiveCharacterTextSplitter]: Produced {len(recursive_chunks)} chunks.")

    print("\n" + "-" * 50)
    print("INSPECTING RECURSIVE CHUNKS (Notice natural sentence/paragraph preservation):")
    print("-" * 50)
    for i, chunk in enumerate(recursive_chunks):
        print(f"\n--- [Chunk #{i+1} | Length: {len(chunk)} chars] ---")
        print(chunk)


def demo_chunk_overlap_importance():
    print("\n" + "=" * 60)
    print("PART 2: Why Chunk Overlap Matters (Preventing Boundary Blind Spots)")
    print("=" * 60)

    short_text = (
        "The server port is 8080. "
        "The admin token is X99-Alpha. "
        "The backup retention policy is 30 days."
    )

    # Split without overlap
    no_overlap_splitter = RecursiveCharacterTextSplitter(chunk_size=35, chunk_overlap=0)
    chunks_no_overlap = no_overlap_splitter.split_text(short_text)

    print("\n[Zero Overlap (chunk_overlap=0)]:")
    for i, c in enumerate(chunks_no_overlap):
        print(f" Chunk {i+1}: '{c}'")

    # Split with overlap
    with_overlap_splitter = RecursiveCharacterTextSplitter(chunk_size=35, chunk_overlap=15)
    chunks_with_overlap = with_overlap_splitter.split_text(short_text)

    print("\n[With Overlap (chunk_overlap=15)] (Overlapping context connects neighbors):")
    for i, c in enumerate(chunks_with_overlap):
        print(f" Chunk {i+1}: '{c}'")


def demo_document_metadata_handling():
    print("\n" + "=" * 60)
    print("PART 3: Creating Document Objects with Rich Metadata")
    print("=" * 60)

    raw_doc = Document(
        page_content=SAMPLE_TECHNICAL_MANUAL,
        metadata={"source": "acme_safety_manual_v4.2.pdf", "category": "Robotics Safety", "classification": "Internal"}
    )

    splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=60)
    split_docs = splitter.split_documents([raw_doc])

    print(f"\nOriginal Document split into {len(split_docs)} Document chunks with propagated metadata:")
    for i, doc in enumerate(split_docs):
        # We can add custom per-chunk metadata like chunk_id
        doc.metadata["chunk_id"] = i + 1
        print(f"\nChunk {i+1} Metadata: {doc.metadata}")
        print(f"Content Preview: {doc.page_content[:90]}...")


if __name__ == "__main__":
    print("\n🚀 Starting Example 05: Document Splitters & Chunking")
    demo_naive_vs_recursive_splitting()
    demo_chunk_overlap_importance()
    demo_document_metadata_handling()
    print("\n✅ Example 05 completed successfully!\n")
