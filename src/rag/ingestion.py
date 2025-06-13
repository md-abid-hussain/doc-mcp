"""Document ingestion pipeline for RAG system."""

import logging
import time
from typing import Callable, List, Optional

from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.embeddings.nebius import NebiusEmbedding
from llama_index.llms.nebius import NebiusLLM

from ..core.config import settings
from ..core.exceptions import IngestionError
from ..database.repository import repository_manager
from ..database.vector_store import get_vector_store
from .models import IngestionProgress

logger = logging.getLogger(__name__)


class DocumentIngestionPipeline:
    """Handles document ingestion with progress tracking."""

    def __init__(
        self, progress_callback: Optional[Callable[[IngestionProgress], None]] = None
    ):
        self.progress_callback = progress_callback
        self.text_splitter = SentenceSplitter(chunk_size=settings.chunk_size)

        # Configure LlamaIndex settings
        Settings.node_parser = self.text_splitter
        Settings.llm = NebiusLLM(
            api_key=settings.nebius_api_key,
            model="meta-llama/Llama-3.3-70B-Instruct-fast",
        )
        Settings.embed_model = NebiusEmbedding(
            api_key=settings.nebius_api_key,
            model_name="BAAI/bge-en-icl",
            embed_batch_size=10,
        )

    def _report_progress(self, progress: IngestionProgress):
        """Report progress to callback if available."""
        if self.progress_callback:
            self.progress_callback(progress)

    async def ingest_documents(
        self, documents: List[Document], repo_name: str, branch: Optional[str] = "main"
    ) -> bool:
        """
        Ingest documents into the vector store.

        Args:
            documents: List of documents to ingest
            repo_name: Repository name for metadata

        Returns:
            True if successful, False otherwise
        """
        if not documents:
            logger.warning("No documents to ingest")
            return False

        start_time = time.time()
        total_docs = len(documents)

        try:
            logger.info(f"Starting ingestion of {total_docs} documents for {repo_name}")

            # Report initial progress
            self._report_progress(
                IngestionProgress(
                    total_documents=total_docs,
                    processed_documents=0,
                    current_phase="Initializing vector store",
                    elapsed_time=0,
                )
            )

            # Get vector store
            vector_store = get_vector_store()
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # Report vector store ready
            self._report_progress(
                IngestionProgress(
                    total_documents=total_docs,
                    processed_documents=0,
                    current_phase="Processing documents",
                    elapsed_time=time.time() - start_time,
                )
            )

            # Create index and ingest documents
            VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                show_progress=True,  # We handle progress ourselves
            )

            # Report completion
            elapsed_time = time.time() - start_time
            self._report_progress(
                IngestionProgress(
                    total_documents=total_docs,
                    processed_documents=total_docs,
                    current_phase="Ingestion complete",
                    elapsed_time=elapsed_time,
                )
            )

            # Update repository metadata
            repository_manager.update_repository_info(repo_name, total_docs, branch)

            logger.info(
                f"Successfully ingested {total_docs} documents for {repo_name} in {elapsed_time:.2f}s"
            )
            return True

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Ingestion failed after {elapsed_time:.2f}s: {e}")

            # Report error
            self._report_progress(
                IngestionProgress(
                    total_documents=total_docs,
                    processed_documents=0,
                    current_phase=f"Error: {str(e)}",
                    elapsed_time=elapsed_time,
                )
            )

            raise IngestionError(f"Document ingestion failed: {e}")


async def ingest_documents_async(
    documents: List[Document],
    repo_name: str,
    progress_callback: Optional[Callable[[IngestionProgress], None]] = None,
    branch: Optional[str] = "main",
) -> bool:
    """
    Async wrapper for document ingestion.

    Args:
        documents: List of documents to ingest
        repo_name: Repository name for metadata
        progress_callback: Optional progress callback

    Returns:
        True if successful, False otherwise
    """
    pipeline = DocumentIngestionPipeline(progress_callback)
    return await pipeline.ingest_documents(documents, repo_name, branch)
