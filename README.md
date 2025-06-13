# 📚 Doc-MCP: Documentation RAG System

A sophisticated system that transforms GitHub documentation repositories into intelligent, queryable knowledge bases using advanced RAG (Retrieval-Augmented Generation) capabilities with MCP (Model Context Protocol) integration.

## 🌟 Features

### 🔄 Two-Step Processing Pipeline
- **Step 1**: Intelligent GitHub repository discovery and file loading
- **Step 2**: Vector embedding generation and MongoDB Atlas storage

### 🧠 Advanced RAG Capabilities
- **Semantic Search**: Vector embeddings using BAAI/bge-en-icl model
- **Multiple Query Modes**: Default (semantic), text search, and hybrid approaches
- **Smart Chunking**: Configurable document chunking with sentence-aware splitting
- **Source Citations**: Full traceability with GitHub file links and relevance scores

### 🚀 Modern Architecture
- **Async Processing**: High-performance concurrent operations for large repositories
- **Real-time Progress**: Live updates during file loading and vector processing
- **Modular Design**: Clean separation of concerns with type safety
- **Error Handling**: Comprehensive error handling with detailed user feedback

### 🖥️ User Interfaces
- **Web Interface**: Beautiful Gradio-based UI with tabbed navigation
- **MCP Server**: Native Model Context Protocol server for AI agents
- **Repository Management**: Complete CRUD operations for ingested repositories

## 🏗️ Architecture Overview

```
doc-mcp/
├── src/
│   ├── core/                 # Core configuration and types
│   │   ├── config.py        # Pydantic settings with env validation
│   │   ├── types.py         # Type definitions and enums
│   │   └── exceptions.py    # Custom exception hierarchy
│   ├── database/            # Database layer
│   │   ├── mongodb.py       # MongoDB client with connection pooling
│   │   ├── vector_store.py  # LlamaIndex MongoDB vector store
│   │   └── repository.py    # Repository metadata management
│   ├── github/              # GitHub integration
│   │   ├── client.py        # Async GitHub API client
│   │   ├── file_loader.py   # Concurrent file loading
│   │   └── parser.py        # URL parsing and validation
│   ├── rag/                 # RAG processing engine
│   │   ├── ingestion.py     # Document processing pipeline
│   │   ├── query.py         # Query retrieval and processing
│   │   └── models.py        # Pydantic models for RAG operations
│   └── ui/                  # User interface
│       ├── app.py           # Main Gradio application
│       ├── components/      # Reusable UI components
│       └── tabs/            # Modular tab implementations
├── scripts/                 # Utility scripts
└── temp/                   # Temporary processing files
```

## 🚀 Quick Start Guide

### Prerequisites

- **Python**: 3.13+ (specified in `.python-version`)
- **MongoDB Atlas**: Vector search enabled cluster
- **API Keys**: 
  - Nebius API key (for embeddings and LLM)
  - GitHub token (optional, for private repos and higher rate limits)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/doc-mcp.git
cd doc-mcp

# Create virtual environment (recommended: use uv for faster installs)
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
# or with uv: uv pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac
```

Edit `.env` with your configuration:

```env
# Required: API Keys
NEBIUS_API_KEY=your_nebius_api_key_here
GITHUB_API_KEY=your_github_token_here

# Required: MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=docmcp
COLLECTION_NAME=doc_rag
REPOS_COLLECTION_NAME=ingested_repos

# Vector Configuration
VECTOR_INDEX_NAME=vector_index
FTS_INDEX_NAME=fts_index
EMBEDDING_DIMENSIONS=4096

# Processing Optimization
CHUNK_SIZE=3072
SIMILARITY_TOP_K=5
GITHUB_CONCURRENT_REQUESTS=10
```

### 3. Database Setup

```bash
# Setup database collections and indexes
python scripts/db_setup.py setup

# Check database status
python scripts/db_setup.py status
```

### 4. Launch Application

```bash
# Start the web interface
python main.py
```

The web interface will be available at `http://localhost:7860`

## 📖 Detailed Usage Guide

### 🔍 Repository Discovery and Ingestion

1. **Navigate to "📥 Documentation Ingestion" tab**
2. **Enter Repository URL**:
   ```
   # Supported formats:
   owner/repo
   https://github.com/owner/repo
   github.com/owner/repo
   ```
3. **Discover Files**: Click "🔍 Discover Documentation Files"
   - Automatically finds `.md` and `.mdx` files
   - Shows file count and repository structure
4. **Select Files**: 
   - Use "📋 Select All Documents" for complete ingestion
   - Or manually select specific files
5. **Execute Pipeline**:
   - **Step 1**: "📥 Step 1: Load Files from GitHub" 
     - Concurrent file downloading with progress tracking
     - Handles large repositories efficiently
   - **Step 2**: "🧠 Step 2: Process & Store Embeddings"
     - Generates vector embeddings using Nebius
     - Stores in MongoDB Atlas with metadata

### 🤖 Intelligent Querying

1. **Go to "🤖 AI Documentation Assistant" tab**
2. **Select Repository**: Choose from ingested repositories
3. **Choose Search Strategy**:
   - **Default**: Semantic similarity (recommended)
   - **Text Search**: Keyword-based matching
   - **Hybrid**: Combined approach for comprehensive results
4. **Ask Questions**: Natural language queries like:
   ```
   "How do I implement authentication?"
   "What are the API rate limits?"
   "Show me examples of custom components"
   ```
5. **Review Results**: Get AI-generated responses with source citations

### 🗂️ Repository Management

1. **Access "🗂️ Repository Management" tab**
2. **View Statistics**: Database size, document counts, collection info
3. **Repository Details**: File counts, last updated, processing status
4. **Delete Repositories**: 
   - Select repository to remove
   - Confirm deletion (irreversible)
   - Automatically updates database

## 🔧 Advanced Configuration

### Vector Store Settings

```python
# src/core/config.py
class Settings(BaseSettings):
    # Embedding configuration
    embedding_dimensions: int = 4096  # BAAI/bge-en-icl dimensions
    chunk_size: int = 3072           # Document chunking size
    similarity_top_k: int = 5        # Results per query
    
    # GitHub optimization
    github_concurrent_requests: int = 10  # Parallel downloads
    github_timeout: int = 30             # Request timeout
    github_retries: int = 3              # Retry attempts
```

### MongoDB Atlas Setup

1. **Create Cluster**: Enable Vector Search in MongoDB Atlas
2. **Database Structure**:
   ```
   Database: docmcp
   ├── doc_rag (documents with embeddings)
   └── ingested_repos (repository metadata)
   ```
3. **Indexes**: Automatically created by the application
   - Vector index for semantic search
   - Full-text search index for keyword queries

### Custom File Extensions

```python
# Modify src/github/file_loader.py
def discover_repository_files(
    repo_url: str, 
    file_extensions: List[str] = [".md", ".mdx", ".rst", ".txt"]
):
    # Add your custom extensions
```

## 🔍 Search Modes Explained

### Default Mode (Semantic)
- Uses vector embeddings for conceptual similarity
- Best for: "How do I..." questions, concept exploration
- Example: "authentication methods" finds OAuth, JWT, API key docs

### Text Search Mode
- Traditional keyword matching
- Best for: Specific terms, exact phrases, code snippets
- Example: "rate_limit" finds exact function names and variables

### Hybrid Mode
- Combines vector and text search results
- Best for: Comprehensive coverage, technical documentation
- Example: Finds both conceptual explanations and implementation details

## 🛠️ Development Guide

### Project Structure Principles

- **Type Safety**: Comprehensive Pydantic models and type hints
- **Async First**: All I/O operations use async/await
- **Error Handling**: Custom exception hierarchy with detailed context
- **Modularity**: Clean separation between UI, business logic, and data layers
- **Configuration**: Environment-based configuration with validation

### Key Components

#### [`src/core/config.py`](src/core/config.py)
- Pydantic settings with environment variable binding
- Validation and default values
- Type-safe configuration access

#### [`src/database/mongodb.py`](src/database/mongodb.py)
- Connection management with lazy initialization
- Error handling and connection testing
- Collection abstractions

#### [`src/github/client.py`](src/github/client.py)
- Async HTTP client with rate limiting
- Concurrent file downloads with semaphores
- Comprehensive error handling for GitHub API

#### [`src/rag/query.py`](src/rag/query.py)
- LlamaIndex integration with MongoDB vector store
- Query mode implementations
- Source citation and metadata processing

#### [`src/ui/app.py`](src/ui/app.py)
- Modular Gradio interface
- Tab-based navigation
- Real-time progress updates

### Adding New Features

1. **New UI Tab**: Extend [`src/ui/tabs/`](src/ui/tabs/) with new tab class
2. **Database Operations**: Add methods to [`RepositoryManager`](src/database/repository.py)
3. **GitHub Features**: Extend [`GitHubClient`](src/github/client.py) for new API calls
4. **RAG Capabilities**: Modify [`DocumentIngestionPipeline`](src/rag/ingestion.py) or [`QueryRetriever`](src/rag/query.py)

## 🔧 Troubleshooting

### Common Issues

1. **Connection Errors**:
   ```bash
   # Test MongoDB connection
   python scripts/db_setup.py status
   ```

2. **GitHub Rate Limits**:
   - Add `GITHUB_API_KEY` for higher limits (5000 vs 60 requests/hour)
   - Reduce `GITHUB_CONCURRENT_REQUESTS` if hitting limits

3. **Memory Issues**:
   - Reduce `CHUNK_SIZE` for large documents
   - Process repositories in smaller batches

4. **Vector Search Not Working**:
   - Verify MongoDB Atlas has Vector Search enabled
   - Check index creation in database
   - Ensure embedding dimensions match (4096 for BAAI/bge-en-icl)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


**Built with ❤️ using modern Python, LlamaIndex, Nebius studio, MongoDB Atlas, and Gradio**

*Transform your documentation into intelligent, queryable knowledge bases with Doc-MCP!*