"""Type definitions for Doc-MCP application."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class QueryMode(str, Enum):
    """Available query modes for document retrieval."""

    DEFAULT = "default"
    TEXT_SEARCH = "text_search"
    HYBRID = "hybrid"


class FileExtensions(str, Enum):
    """Supported file extensions."""

    MARKDOWN = ".md"
    MARKDOWN_X = ".mdx"
    TEXT = ".txt"
    RESTRUCTURED_TEXT = ".rst"


class ProcessingStatus(str, Enum):
    """Processing status indicators."""

    PENDING = "pending"
    LOADING = "loading"
    LOADED = "loaded"
    VECTORIZING = "vectorizing"
    COMPLETE = "complete"
    ERROR = "error"


class DocumentMetadata(BaseModel):
    """Document metadata structure."""

    file_path: str
    file_name: str
    file_extension: str
    directory: str
    repo: str
    branch: str
    sha: str
    size: int
    url: str
    raw_url: str
    type: str = "file"


class GitHubFileInfo(BaseModel):
    """GitHub file information."""

    path: str
    name: str
    sha: str
    size: int
    url: str
    download_url: str
    type: str
    encoding: str
    content: str


class ProgressState(BaseModel):
    """Progress tracking for operations."""

    status: ProcessingStatus
    message: str
    progress: float = Field(ge=0, le=100)
    phase: str = ""
    details: str = ""
    step: str = ""
    total_files: int = 0
    processed_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    error: Optional[str] = None
    repository_updated: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class RepositoryInfo(BaseModel):
    """Repository information structure."""

    name: str
    branch: str = "main"
    total_files: int = 0
    ingested_files: int = 0
    last_updated: datetime
    status: ProcessingStatus = ProcessingStatus.PENDING
