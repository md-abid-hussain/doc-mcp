# 📚 Doc-MCP: Documentation RAG System

Transform GitHub documentation repositories into intelligent, queryable knowledge bases using RAG and MCP with automated workflow orchestration via Kestra.

## 🎥 Demo Video

[![Doc-MCP Demo](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRceMtWa5sWvcpsHVn6e7tFSwI3TfI6a2xp8Q&s)](https://youtu.be/54fX3fZg73Q)



## ✨ Features

- **Semantic Search** - Find answers across documentation using natural language
- 🤖 **AI-Powered Q&A** - Get intelligent responses with source citations
- 📚 **Batch Processing** - Ingest entire repositories with progress tracking
- 🔄 **Incremental Updates** - Detect and sync only changed files
- 🗂️ **Repository Management** - Complete CRUD operations for ingested docs
- ⚙️ **Workflow Orchestration** - Automated document ingestion with Kestra
- 📅 **Scheduled Processing** - Daily automated updates for tracked repositories

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **MongoDB Atlas** with Vector Search enabled
- **Nebius API key** for embeddings and LLM
- **GitHub token** (optional, for private repos and higher rate limits)
- **Docker & Docker Compose** (for Kestra workflows)

### Installation

```bash
# Clone and setup
git clone https://github.com/md-abid-hussain/doc-mcp.git
cd doc-mcp
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Setup environment
cp .env.example .env
```

Edit `.env` with your credentials:
```env
NEBIUS_API_KEY=your_nebius_api_key_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
GITHUB_API_KEY=your_github_token_here  # Optional

# Kestra Configuration
KESTRA_HOSTNAME=http://localhost:8080
KESTRA_USER=admin@localhost.dev
KESTRA_PASSWORD=kestra
```

### Launch

```bash
# Setup database
python scripts/db_setup.py setup

# Start application
python main.py
```

Visit `http://localhost:7860` to access the web interface.

Access MCP at `http://127.0.0.1:7860/gradio_api/mcp/sse`

## 🔧 Kestra Workflow Setup (Optional)

Kestra provides automated workflow orchestration for document ingestion with scheduled updates and change detection.

### 1. Start Kestra Server

Follow the [Kestra Quickstart Guide](https://kestra.io/docs/getting-started/quickstart) to set up Kestra:

```bash
# Download and start Kestra
curl -o docker-compose.yml \
  https://raw.githubusercontent.com/kestra-io/kestra/develop/docker-compose.yml
```

Access Kestra UI at `http://localhost:8080`

### 2. Configure Secrets

Before starting kestra, configure secrets in Kestra following the [Secrets Documentation](https://kestra.io/docs/concepts/secret) in kestra docker compose file.



```yaml
# Required Secrets
MONGO_URI: "your_mongodb_uri"
DB: "docmcp"
COLLECTION_NAME: "ingested_repos"
VECTOR_COLLECTION_NAME: "doc_rag"
NEBIUS_API_KEY: "your_nebius_api_key_here"
GITHUB_API_TOKEN: "your_github_token_here"
```
```yaml
# Start Kestra
docker-compose up -d
```

### 3. Import Workflows

Import the provided Kestra workflows:

1. **Copy workflow files** from `kestra_flow/` directory
2. **Import via Kestra UI**:
   - Go to `Flows` in Kestra UI
   - Click `Import`
   - Import both workflows:
     - `company.team.repo-ingestion-controller.yml`
     - `company.team.single-repo-ingestion.yml`

### 4. Workflow Features

#### 🔄 Repo Ingestion Controller
- **Purpose**: Batch processing of all tracked repositories
- **Schedule**: Runs daily at midnight (`@daily`)
- **Function**: Checks all repositories with `tracking_enabled: true`
- **Concurrency**: Processes up to 3 repositories simultaneously

#### 📦 Single Repo Ingestion
- **Purpose**: Process individual repository updates
- **Features**:
  - Detects file changes using SHA comparison
  - Incremental updates (only changed files)
  - Automatic cleanup of outdated documents
  - Repository metadata tracking

### 5. Using Kestra UI in Doc-MCP

Once Kestra is running, use the "⚙️ Kestra Workflows" tab in Doc-MCP:

1. **Check Server Status**: Verify Kestra connection
2. **Batch Processing**: Trigger `repo-ingestion-controller` for all repositories
3. **Single Repository**: Select and process individual repositories from database
4. **Monitor Execution**: View real-time status and logs

## Usage

### 1. Ingest Documentation
- Navigate to "📥 Documentation Ingestion" tab
- Enter GitHub repository URL (e.g., `owner/repo`)
- Select markdown files to process
- Execute two-step pipeline: Load files → Generate embeddings

### 2. Query Documentation  
- Go to "🤖 AI Documentation Assistant" tab
- Select your repository
- Ask natural language questions
- Get AI responses with source citations

### 3. Manage Repositories
- Use "🗂️ Repository Management" tab  
- View statistics and file counts
- Delete repositories when needed

### 4. Automated Workflows (with Kestra)
- Use "⚙️ Kestra Workflows" tab
- Monitor automated daily ingestion
- Trigger manual updates for specific repositories
- View workflow execution logs and status

## 🔧 Configuration

### Environment Variables

```env
# Required
NEBIUS_API_KEY=your_nebius_api_key_here
MONGODB_URI=your_mongodb_uri

# Optional
GITHUB_API_KEY=your_github_token_here
CHUNK_SIZE=3072
SIMILARITY_TOP_K=5
GITHUB_CONCURRENT_REQUESTS=10

# Kestra (Optional)
KESTRA_HOSTNAME=http://localhost:8080
KESTRA_USER=admin@localhost.dev
KESTRA_PASSWORD=kestra
KESTRA_API_TOKEN=your_api_token  # Alternative to user/password
```

### MongoDB Atlas Setup

1. Create cluster with **Vector Search** enabled
2. Database structure auto-created:
   - `doc_rag` - documents with embeddings  
   - `ingested_repos` - repository metadata

### Kestra Workflow Configuration

The workflows support these MongoDB collections:
- **Documents**: `doc_rag` (configurable via `VECTOR_COLLECTION_NAME`)
- **Repositories**: `ingested_repos` (configurable via `COLLECTION_NAME`)

## 🔄 Automated Change Detection

### How It Works

1. **Daily Schedule**: Kestra runs the controller workflow daily
2. **Change Detection**: Compares GitHub file SHAs with stored versions
3. **Incremental Updates**: Only processes modified files
4. **Cleanup**: Removes outdated document versions
5. **Metadata Sync**: Updates repository tracking information

### Benefits

- **Efficiency**: Only processes changed files
- **Consistency**: Keeps documentation in sync with source
- **Automation**: No manual intervention required
- **Scalability**: Handles multiple repositories concurrently

## 🐛 Troubleshooting

**Common Issues:**

- **Rate Limits**: Add GitHub token for 5000 requests/hour (vs 60)
- **Memory Issues**: Reduce `CHUNK_SIZE` in `.env`
- **Connection Errors**: Verify MongoDB Atlas Vector Search is enabled
- **Database Issues**: Run `python scripts/db_setup.py status`

**Kestra-Specific Issues:**

- **Workflow Import Fails**: Verify all secrets are configured
- **Execution Errors**: Check Kestra logs via `docker-compose logs kestra`
- **Connection Issues**: Ensure Kestra is running on port 8080
- **Secret Access**: Verify secret names match exactly in workflows

## 📖 Documentation

For detailed guides see:
- Advanced configuration options
- Development and contribution guide  
- API reference and examples
- [Kestra Documentation](https://kestra.io/docs) for workflow customization

## 💻 Author

**Md Abid Hussain**
- GitHub: [@md-abid-hussain](https://github.com/md-abid-hussain)
- LinkedIn: [md-abid-hussain](https://www.linkedin.com/in/md-abid-hussain-52862b229/)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Python, LlamaIndex, Nebius, MongoDB Atlas, Gradio, and Kestra**