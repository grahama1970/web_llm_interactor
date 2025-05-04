# 🧠 GitGit Advanced Parsing Requirements

This document outlines the requirements and implementation details for the enhanced GitGit functionality that provides optimized repository information for LLM agents.

## 🎯 Core Objective

Create an enhanced version of GitGit that processes repository content with advanced parsing techniques to provide highly structured, queryable information to LLM agents while preserving all important code relationships and hierarchies.

## 📄 Output Format Requirements

1. **Primary Output**:
   - A single concatenated markdown file (maintaining current behavior)
   - Structured with clear section hierarchy and code relationships
   - Proper formatting that preserves code blocks, indentation, and markup

2. **Intermediate Storage**:
   - Intermediate parsed markdown files stored in a dedicated directory
   - Organized to reflect the original repository structure
   - Preserved for potential direct access by agents

3. **Section Identification**:
   - Each section must have a hash field (not UUID4)
   - Hashes must be stable across runs for the same content
   - Use the same hashing approach as in markdown_extractor.py
   - Designed to enable targeted database insertion and querying

## 🖥️ CLI Interface Guidelines

1. **Simplicity First**:
   - Keep parameters minimal to avoid confusing agents
   - Default to enabling all advanced features without explicit flags
   - Focus on the most common use cases

2. **Advanced Functionality**:
   - Tree-sitter parsing should be enabled by default
   - Text chunking should be built-in automatically
   - Section hierarchy preservation should happen automatically

3. **Command Pattern**:
   - Maintain current command pattern: `gitgit analyze repo-url`
   - Add minimal parameters only when absolutely necessary
   - Provide clear help text for all parameters

## 🏗️ Structural Requirements

1. **Repository Structure**:
   - Preserve file/folder structure from sparse download
   - Maintain relationships between files/directories
   - Reflect imports, dependencies and project organization

2. **Document Structure**:
   - Preserve section hierarchy within each file
   - Maintain code block relationships with descriptions
   - Keep indentation and formatting intact

3. **Code Structure**:
   - Extract function/class definitions with parameters and types
   - Preserve docstrings and their relationships to code
   - Maintain code structure for better understanding

## 🔄 Future Integration Path

1. **API Integration**:
   - Design with future FastAPI + MCP integration in mind
   - Use the fastapi_mcp_sse pattern as a reference
   - Enable core functionality to be exposed via API endpoints

2. **Database Integration**:
   - Section hashes enable future database storage of sections
   - Structure output to facilitate database insertion
   - Support relationship mapping in a graph database

## 📊 Verification Requirements

1. **Rich Table Output**:
   - Use rich tables for displaying section hierarchy
   - Include clear verification status columns
   - Show both expected and actual values

2. **Executable Verification**:
   - Every component must have runnable verification
   - Clear pass/fail indication with detailed error information
   - Human-readable output that's easy to interpret

3. **Concrete Examples**:
   - Use real repositories (e.g., python-arango) for verification
   - Show actual output instead of hypothetical examples
   - Document expected results for key test cases

## 📦 Implementation Reference

Use the archived code as a reference:
- `_archive/gitgit/markdown_extractor.py` for markdown parsing
- `_archive/gitgit/text_chunker.py` for text chunking logic
- `_archive/gitgit/tree_sitter_utils.py` for code structure extraction

## 🔍 Success Criteria

A successful implementation will:
1. Process repository content while preserving all structural relationships
2. Extract code structure with parameters, types, and docstrings
3. Maintain section hierarchy with UUIDs for database insertion
4. Provide both concatenated output and individual processed files
5. Present information in an optimal format for LLM agent consumption
6. Have detailed verification that demonstrates correct functionality
7. Keep a simple CLI interface that agents can easily use