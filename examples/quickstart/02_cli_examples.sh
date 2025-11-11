#!/bin/bash
# Gideon CLI Examples
# ===================
# This script demonstrates common CLI usage patterns

echo "================================"
echo "Gideon CLI Examples"
echo "================================"

# Example 1: Index documents for search
echo -e "\n1. Indexing documents..."
echo "   Command: gideon search index ./documents/"
echo "   This creates a searchable index of all PDFs"

# Example 2: Semantic search
echo -e "\n2. Semantic search..."
echo "   Command: gideon search search 'transformer architectures' --top-k 5"
echo "   Finds the 5 most relevant papers about transformers"

# Example 3: Ask questions (RAG)
echo -e "\n3. Q&A with RAG..."
echo "   Command: gideon search ask 'What are attention mechanisms?'"
echo "   Get AI-powered answers from your document collection"

# Example 4: Rename files with AI
echo -e "\n4. Auto-rename documents..."
echo "   Command: gideon rename auto ./papers/"
echo "   AI extracts metadata and generates clean filenames"

# Example 5: Smart duplicate detection
echo -e "\n5. Find duplicates..."
echo "   Command: gideon deduplicate scan ./papers/ --mode all"
echo "   Detects exact and version duplicates"

# Example 6: Organize by topics
echo -e "\n6. Organize files..."
echo "   Command: gideon organize ./papers/"
echo "   Sorts files into topic-based folders"

# Example 7: Find similar documents
echo -e "\n7. Find similar papers..."
echo "   Command: gideon search similar paper.pdf --top-k 10"
echo "   Finds papers similar to a reference document"

# Example 8: Full workflow
echo -e "\n8. Complete workflow..."
echo "   # Step 1: Rename files"
echo "   gideon rename auto ./new_papers/"
echo ""
echo "   # Step 2: Remove duplicates"
echo "   gideon deduplicate scan ./new_papers/ --remove"
echo ""
echo "   # Step 3: Organize"
echo "   gideon organize ./new_papers/"
echo ""
echo "   # Step 4: Index for search"
echo "   gideon search index ./new_papers/"

echo -e "\n================================"
echo "For more info: gideon --help"
echo "================================"
