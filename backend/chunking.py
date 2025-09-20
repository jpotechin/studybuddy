"""
Intelligent text chunking module for PDF and TXT imports.

This module provides intelligent chunking strategies that respect document structure,
sentence boundaries, and include overlap to prevent information loss.
"""

import re
from typing import Generator, List


def chunk_text_intelligently(text: str, target_chunk_size: int = 1000, overlap_size: int = 100) -> Generator[str, None, None]:
    """
    Intelligently chunk text by respecting sentence and paragraph boundaries.
    
    Args:
        text: Input text to chunk
        target_chunk_size: Target number of words per chunk
        overlap_size: Number of words to overlap between chunks
    
    Returns:
        Generator of text chunks
    """
    # First, try to detect document structure (headers, sections, etc.)
    text = preprocess_text_for_chunking(text)
    
    # Split into paragraphs first
    paragraphs = text.split('\n\n')
    current_chunk = ""
    current_word_count = 0
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Count words in this paragraph
        paragraph_words = len(paragraph.split())
        
        # If adding this paragraph would exceed target size, yield current chunk
        if current_word_count + paragraph_words > target_chunk_size:
            if current_chunk:
                # Try to break at sentence boundary within the paragraph
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                remaining_space = target_chunk_size - current_word_count
                
                # Add complete sentences that fit
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    if current_word_count + sentence_words <= target_chunk_size:
                        current_chunk += " " + sentence
                        current_word_count += sentence_words
                    else:
                        break
                
                # Yield the chunk
                yield current_chunk.strip()
                
                # Start new chunk with overlap
                overlap_text = get_overlap_text(current_chunk, overlap_size)
                current_chunk = overlap_text
                current_word_count = len(overlap_text.split()) if overlap_text else 0
                
                # Add remaining sentences from the paragraph
                remaining_sentences = sentences[len([s for s in sentences if len(s.split()) <= remaining_space]):]
                for sentence in remaining_sentences:
                    current_chunk += " " + sentence
                    current_word_count += len(sentence.split())
            else:
                # Current chunk is empty but paragraph is too large - split it
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                temp_chunk = ""
                temp_word_count = 0
                
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    if temp_word_count + sentence_words <= target_chunk_size:
                        temp_chunk += " " + sentence if temp_chunk else sentence
                        temp_word_count += sentence_words
                    else:
                        # Yield this chunk and start a new one
                        if temp_chunk:
                            yield temp_chunk.strip()
                            # Start new chunk with overlap
                            overlap_text = get_overlap_text(temp_chunk, overlap_size)
                            temp_chunk = overlap_text
                            temp_word_count = len(overlap_text.split()) if overlap_text else 0
                        # Add current sentence to new chunk
                        temp_chunk += " " + sentence if temp_chunk else sentence
                        temp_word_count += sentence_words
                
                current_chunk = temp_chunk
                current_word_count = temp_word_count
        else:
            # Add the whole paragraph
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
            current_word_count += paragraph_words
    
    # Yield the last chunk if it has content
    if current_chunk.strip():
        yield current_chunk.strip()


def preprocess_text_for_chunking(text: str) -> str:
    """
    Preprocess text to improve chunking quality by detecting structure.
    
    Args:
        text: Raw text to preprocess
        
    Returns:
        Preprocessed text with better structure detection
    """
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Detect and preserve headers (lines that are all caps or start with numbers)
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('')
            continue
            
        # Check if this looks like a header
        if (len(line) < 100 and 
            (line.isupper() or 
             re.match(r'^\d+\.?\s+[A-Z]', line) or  # "1. Introduction" or "1 Introduction"
             re.match(r'^[A-Z][a-z]+\s+[A-Z]', line) or  # "Chapter 1" or "Section A"
             re.match(r'^\d+\.\d+', line))):  # "1.1" or "2.3"
            # Add extra spacing around headers
            processed_lines.append(f'\n{line}\n')
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)


def get_overlap_text(text: str, overlap_size: int) -> str:
    """
    Get the last 'overlap_size' words from text for overlap between chunks.
    
    Args:
        text: Text to extract overlap from
        overlap_size: Number of words to overlap
        
    Returns:
        Overlap text (last N words)
    """
    words = text.split()
    if len(words) <= overlap_size:
        return text
    return " ".join(words[-overlap_size:])


def chunk_text_simple(words: List[str], chunk_size: int) -> Generator[str, None, None]:
    """
    Simple fixed-length chunking for backward compatibility.
    
    Args:
        words: List of words to chunk
        chunk_size: Number of words per chunk
        
    Returns:
        Generator of text chunks
    """
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])


def get_chunking_stats(chunks: List[str], total_words: int) -> dict:
    """
    Calculate and return chunking statistics.
    
    Args:
        chunks: List of text chunks
        total_words: Original number of words in the text
        
    Returns:
        Dictionary with chunking statistics
    """
    chunk_sizes = [len(chunk.split()) for chunk in chunks]
    total_processed_words = sum(chunk_sizes)
    overlap_words = total_processed_words - total_words
    
    return {
        'chunk_sizes': chunk_sizes,
        'total_processed_words': total_processed_words,
        'overlap_words': overlap_words,
        'average_chunk_size': sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0,
        'num_chunks': len(chunks)
    }


def print_chunking_info(total_words: int, chunk_size: int, overlap_size: int, 
                       use_simple: bool, chunks: List[str]):
    """
    Print chunking information and statistics.
    
    Args:
        total_words: Original number of words
        chunk_size: Target chunk size
        overlap_size: Overlap size
        use_simple: Whether using simple chunking
        chunks: List of chunks
    """
    num_chunks = len(chunks)
    
    print(f"Document has {total_words} words → will be processed in {num_chunks} chunks")
    print(f"Chunk size: {chunk_size} words, Overlap: {overlap_size} words")
    
    if not use_simple:
        stats = get_chunking_stats(chunks, total_words)
        print(f"Chunk sizes: {stats['chunk_sizes']}")
        print(f"Average chunk size: {stats['average_chunk_size']:.1f} words")
        print(f"Total processed: {stats['total_processed_words']} words (includes {stats['overlap_words']} overlap words)")
        print(f"📝 Note: Overlap ensures no information is lost at chunk boundaries")
