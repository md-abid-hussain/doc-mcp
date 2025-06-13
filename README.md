# 📚 Doc-MCP: Documentation RAG System

A sophisticated system for transforming GitHub documentation repositories into accessible MCP (Model Context Protocol) servers with advanced RAG (Retrieval-Augmented Generation) capabilities.

## 🌟 Features

- **📥 GitHub Integration**: Seamlessly fetch documentation from any GitHub repository
- **🧠 Advanced RAG**: Vector embeddings with MongoDB Atlas for intelligent document retrieval
- **🔍 Multiple Search Modes**: Semantic similarity, keyword search, and hybrid approaches
- **🖥️ Modern UI**: Beautiful Gradio interface for easy interaction
- **🔧 MCP Server**: Transform documentation into MCP servers for AI agents
- **📊 Repository Management**: Track, manage, and delete ingested repositories
- **⚡ Async Processing**: High-performance async operations for large repositories

## 🏗️ Architecture

```
doc-mcp-refactored/
├── src/
│   ├── core/           # Configuration, types, exceptions
│   ├── database/       # MongoDB operations and vector store
│   ├── github/         # GitHub API client and file handling
│   ├── rag/           # Document ingestion and query processing
│   ├── mcp/           # Model Context Protocol server
│   └── ui/            # Gradio web interface
├── scripts/           # Utility scripts
└── docs/             # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- MongoDB Atlas account
- GitHub API token (optional, for private repositories)
- Nebius API key for embeddings

### Installation

1. **Clone and setup**:
```bash
cd doc-mcp-refactored
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
copy .env.example .env
# Edit .env with your API keys and MongoDB URI
```

3. **Run the application**:
```bash
python -m src.ui.app
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEBIUS_API_KEY` | Nebius API key for embeddings | ✅ |
| `MONGODB_URI` | MongoDB Atlas connection string | ✅ |
| `GITHUB_API_KEY` | GitHub token for API access | ⚠️ |
| `DB_NAME` | Database name | ❌ |
| `CHUNK_SIZE` | Text chunking size | ❌ |
| `SIMILARITY_TOP_K` | Number of results to return | ❌ |

### Database Setup

1. Create a MongoDB Atlas cluster
2. Create a database and collections
3. Set up vector search indexes (automatically handled)

## 📖 Usage

### Web Interface

1. **Documentation Ingestion**:
   - Enter GitHub repository URL
   - Select documentation files
   - Process through 2-step pipeline

2. **Query Interface**:
   - Select ingested repository
   - Choose search mode
   - Ask natural language questions

3. **Repository Management**:
   - View statistics
   - Manage repositories
   - Delete unwanted data

### MCP Server

Run as an MCP server for AI agents:

```bash
python -m src.mcp.server
```

### Programmatic Access

```python
from src.rag.query import create_query_retriever
from src.github.file_loader import load_files_from_github
from src.rag.ingestion import ingest_documents_async

# Load documents from GitHub
documents, failed = await load_files_from_github(
    "owner/repo", 
    ["README.md", "docs/guide.md"]
)

# Ingest into vector store
await ingest_documents_async(documents, "owner/repo")

# Query the repository
retriever = create_query_retriever("owner/repo")
result = retriever.make_query("How do I get started?")
```

## 🔍 Search Modes

- **Default**: Semantic similarity using vector embeddings
- **Text Search**: Traditional keyword-based search
- **Hybrid**: Combines vector and text search for best results

## 🛠️ Development

### Project Structure

- **Core**: Configuration management, type definitions, custom exceptions
- **Database**: MongoDB client, vector store operations, repository management
- **GitHub**: API client, file loading, URL parsing
- **RAG**: Document ingestion pipeline, query processing
- **MCP**: Model Context Protocol server implementation
- **UI**: Gradio interface with modular tabs

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
black src/
isort src/
mypy src/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/doc-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/doc-mcp/discussions)
- **Documentation**: [Full Documentation](docs/)

## 🚀 Roadmap

- [ ] Support for additional file formats (PDF, DOCX)
- [ ] Integration with more embedding providers
- [ ] Advanced query optimization
- [ ] Collaborative features
- [ ] Enterprise deployment options

---

**Built with ❤️ for the AI community**
