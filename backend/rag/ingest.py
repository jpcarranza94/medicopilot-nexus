#!/usr/bin/env python3
"""
Document ingestion and processing module.

Handles PDF extraction, chunking, and metadata extraction for:
- GPC (Clinical Practice Guidelines)
- COFEPRIS (Pharmaceutical Registry)
"""

import os
import re
from typing import List, Dict, Optional
import logging

try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    import fitz

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process medical documents for RAG ingestion."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 80):
        """
        Initialize DocumentProcessor.

        Args:
            chunk_size: Target size for text chunks (characters)
            chunk_overlap: Overlap between consecutive chunks (characters)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_document(self, file_path: str, namespace: str) -> List[Dict]:
        """
        Process a document based on its type.

        Args:
            file_path: Path to the PDF file
            namespace: Document namespace ("gpc", "cofepris", "plm")

        Returns:
            List of chunk dictionaries with text and metadata
        """
        logger.info(f"Processing document: {file_path} (namespace: {namespace})")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")

        filename = os.path.basename(file_path)
        document_name = os.path.splitext(filename)[0]

        if namespace == "cofepris":
            return self._process_cofepris(file_path, document_name, namespace)
        else:  # gpc, plm, or other
            return self._process_gpc(file_path, document_name, namespace)

    def _extract_pdf_text(self, file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from PDF with page numbers.

        Returns:
            List of dicts with 'page_number' and 'text'
        """
        pages = []

        try:
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text()
                pages.append({
                    "page_number": page_num,
                    "text": text
                })
            doc.close()
            logger.info(f"Extracted {len(pages)} pages from {file_path}")
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise

        return pages

    def _process_gpc(self, file_path: str, document_name: str, namespace: str) -> List[Dict]:
        """
        Process GPC (Clinical Practice Guidelines) document.

        Uses semantic chunking to preserve clinical context.
        """
        pages = self._extract_pdf_text(file_path)
        chunks = []

        for page_data in pages:
            page_num = page_data["page_number"]
            text = page_data["text"]

            # Skip very short pages (likely cover pages)
            if len(text.strip()) < 100:
                continue

            # Split into chunks
            page_chunks = self._split_into_chunks(text)

            for chunk_text in page_chunks:
                # Extract metadata from chunk
                section = self._extract_section_name(chunk_text)
                evidence_level = self._extract_evidence_level(chunk_text)

                chunk = {
                    "text": chunk_text,
                    "source_type": "gpc" if namespace == "gpc" else namespace,
                    "document_name": document_name,
                    "page_number": page_num,
                    "namespace": namespace,
                    "section": section,
                    "evidence_level": evidence_level,
                }

                chunks.append(chunk)

        logger.info(f"Created {len(chunks)} chunks from {document_name}")
        return chunks

    def _process_cofepris(self, file_path: str, document_name: str, namespace: str) -> List[Dict]:
        """
        Process COFEPRIS pharmaceutical registry document.

        Extracts tabular data and groups ~50 medications per chunk for efficiency.
        """
        all_medications = []

        # Try pdfplumber first for better table extraction
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        tables = page.extract_tables()

                        for table in tables:
                            if not table or len(table) < 2:
                                continue

                            # First row is usually headers
                            headers = table[0]

                            # Process each medication row
                            for row in table[1:]:
                                if len(row) < 4:  # Skip incomplete rows
                                    continue

                                # Parse row into text
                                row_text = self._parse_cofepris_row_to_text(headers, row)
                                if row_text:
                                    all_medications.append({
                                        'text': row_text,
                                        'page_num': page_num
                                    })

                logger.info(f"Extracted {len(all_medications)} medication entries from {document_name}")

                # Now group into larger chunks (25 medications per chunk)
                chunks = []
                chunk_size = 25

                for i in range(0, len(all_medications), chunk_size):
                    batch = all_medications[i:i + chunk_size]

                    # Combine all medication texts
                    combined_text = "\n\n".join([med['text'] for med in batch])

                    # Use first medication's page for reference
                    page_num = batch[0]['page_num'] if batch else 1

                    chunk = {
                        "text": combined_text,
                        "source_type": "cofepris",
                        "document_name": document_name,
                        "page_number": page_num,
                        "namespace": namespace,
                        "section": f"Medications {i+1}-{i+len(batch)}",
                        "evidence_level": None,
                        "generic_name": None,  # Multiple medications, can't specify one
                        "brand_name": None,
                        "manufacturer": None,
                    }

                    chunks.append(chunk)

                logger.info(f"Created {len(chunks)} chunks from {len(all_medications)} medications ({chunk_size} meds/chunk)")
                return chunks

            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}, falling back to text extraction")

        # Fallback: Use text extraction
        pages = self._extract_pdf_text(file_path)

        for page_data in pages:
            page_num = page_data["page_number"]
            text = page_data["text"]

            # Simple text-based chunking for COFEPRIS
            lines = text.split('\n')
            current_chunk = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                current_chunk.append(line)

                # Create chunk when we have enough lines or detect a new entry
                if len(' '.join(current_chunk)) > self.chunk_size:
                    chunk_text = ' '.join(current_chunk)

                    chunk = {
                        "text": chunk_text,
                        "source_type": "cofepris",
                        "document_name": document_name,
                        "page_number": page_num,
                        "namespace": namespace,
                        "generic_name": self._extract_generic_name(chunk_text),
                        "brand_name": None,
                        "manufacturer": None,
                    }

                    chunks.append(chunk)
                    current_chunk = []

        logger.info(f"Created {len(chunks)} chunks from {document_name}")
        return chunks

    def _parse_cofepris_row_to_text(self, headers: List[str], row: List[str]) -> Optional[str]:
        """Parse a single row from COFEPRIS table to text format."""
        try:
            # Build a text representation with non-empty values
            parts = []
            for h, v in zip(headers, row):
                if v and v.strip():  # Only include non-empty values
                    parts.append(f"{h}: {v}")

            if parts:
                return ' | '.join(parts)
            return None

        except Exception as e:
            logger.warning(f"Error parsing COFEPRIS row: {e}")
            return None

    def _parse_cofepris_row(self, headers: List[str], row: List[str],
                            page_num: int, document_name: str, namespace: str) -> Optional[Dict]:
        """Parse a single row from COFEPRIS table (legacy method - kept for compatibility)."""
        try:
            # Build a text representation
            row_text = ' | '.join([f"{h}: {v}" for h, v in zip(headers, row) if v])

            # Extract key fields (adjust indices based on actual table structure)
            generic_name = None
            brand_name = None
            manufacturer = None

            for i, header in enumerate(headers):
                if i >= len(row):
                    break

                header_lower = header.lower() if header else ""
                value = row[i] if row[i] else None

                if "genérica" in header_lower or "denominación genérica" in header_lower:
                    generic_name = value
                elif "distintiva" in header_lower or "marca" in header_lower:
                    brand_name = value
                elif "titular" in header_lower or "fabricante" in header_lower:
                    manufacturer = value

            return {
                "text": row_text,
                "source_type": "cofepris",
                "document_name": document_name,
                "page_number": page_num,
                "namespace": namespace,
                "generic_name": generic_name,
                "brand_name": brand_name,
                "manufacturer": manufacturer,
            }

        except Exception as e:
            logger.warning(f"Error parsing COFEPRIS row: {e}")
            return None

    def _split_into_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks at sentence boundaries.

        Args:
            text: Input text

        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        # Split into sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence exceeds chunk_size, start a new chunk
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))

                # Keep overlap
                overlap_text = ' '.join(current_chunk)
                if len(overlap_text) > self.chunk_overlap:
                    # Start new chunk with last few sentences for overlap
                    overlap_sentences = []
                    overlap_length = 0
                    for s in reversed(current_chunk):
                        if overlap_length + len(s) <= self.chunk_overlap:
                            overlap_sentences.insert(0, s)
                            overlap_length += len(s)
                        else:
                            break
                    current_chunk = overlap_sentences
                    current_length = overlap_length
                else:
                    current_chunk = []
                    current_length = 0

            current_chunk.append(sentence)
            current_length += sentence_length

        # Add remaining chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def _extract_section_name(self, text: str) -> Optional[str]:
        """
        Extract section name from chunk text.

        Looks for common section headers in GPC documents.
        """
        section_patterns = [
            r'(?i)(diagnóstico|diagnosis)',
            r'(?i)(tratamiento|treatment)',
            r'(?i)(metodología|methodology)',
            r'(?i)(recomendaciones|recommendations)',
            r'(?i)(evidencia|evidence)',
            r'(?i)(algoritmo|algorithm)',
            r'(?i)(introducción|introduction)',
        ]

        for pattern in section_patterns:
            match = re.search(pattern, text[:200])  # Check first 200 chars
            if match:
                return match.group(1).lower()

        return None

    def _extract_evidence_level(self, text: str) -> Optional[str]:
        """
        Extract evidence level (A, B, C, D) from chunk text.

        Looks for NICE, GRADE, or other evidence rating systems.
        """
        # Look for evidence levels like "Nivel A", "Grade B", etc.
        patterns = [
            r'(?i)nivel\s+([A-D])',
            r'(?i)grade\s+([A-D])',
            r'(?i)evidencia\s+([A-D])',
            r'\b([A-D])\s*(?=recomendación|recommendation)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).upper()

        return None

    def _extract_generic_name(self, text: str) -> Optional[str]:
        """Extract generic drug name from text."""
        # Simple extraction - looks for common drug name patterns
        # This is a simplified version; production would be more sophisticated

        patterns = [
            r'(?i)(?:genérico|generic):\s*([A-Za-zá-ú]+)',
            r'(?i)(?:principio activo|active ingredient):\s*([A-Za-zá-ú]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None
