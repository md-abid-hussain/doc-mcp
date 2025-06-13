"""File loading logic for GitHub repositories."""

import logging
from typing import List, Tuple

from llama_index.core import Document

from ..core.exceptions import GitHubError
from ..core.types import DocumentMetadata, GitHubFileInfo
from .client import github_client
from .parser import build_github_web_url, parse_github_url

logger = logging.getLogger(__name__)


def create_document_from_file_info(
    file_info: GitHubFileInfo, repo_name: str, branch: str = "main"
) -> Document:
    """Create a LlamaIndex Document from GitHub file info."""

    try:
        owner, repo = parse_github_url(repo_name)
        web_url = build_github_web_url(owner, repo, file_info.path, branch)
    except Exception:
        web_url = file_info.url

    # Create document metadata
    metadata = DocumentMetadata(
        file_path=file_info.path,
        file_name=file_info.name,
        file_extension=file_info.path.split(".")[-1] if "." in file_info.path else "",
        directory=(
            "/".join(file_info.path.split("/")[:-1]) if "/" in file_info.path else ""
        ),
        repo=repo_name,
        branch=branch,
        sha=file_info.sha,
        size=file_info.size,
        url=web_url,
        raw_url=file_info.download_url,
        type=file_info.type,
    )

    # Create LlamaIndex document
    document = Document(
        text=file_info.content,
        doc_id=f"{repo_name}:{branch}:{file_info.path}",
        metadata=metadata.dict(),
    )

    return document


async def load_files_from_github(
    repo_url: str, file_paths: List[str], branch: str = "main", max_concurrent: int = 10
) -> Tuple[List[Document], List[str]]:
    """
    Load multiple files from GitHub repository.

    Args:
        repo_url: GitHub repository URL or owner/repo format
        file_paths: List of file paths to load
        branch: Git branch name
        max_concurrent: Maximum concurrent requests

    Returns:
        Tuple of (loaded_documents, failed_file_paths)
    """
    if not file_paths:
        logger.warning("No file paths provided")
        return [], []

    try:
        # Parse repo name for metadata
        owner, repo = parse_github_url(repo_url)
        repo_name = f"{owner}/{repo}"
    except Exception as e:
        raise GitHubError(f"Invalid repository URL: {e}")

    logger.info(f"Loading {len(file_paths)} files from {repo_name}")

    # Fetch files from GitHub
    file_infos, failed_paths = await github_client.get_multiple_files(
        repo_url, file_paths, branch, max_concurrent
    )

    # Convert to LlamaIndex documents
    documents = []
    for file_info in file_infos:
        try:
            document = create_document_from_file_info(file_info, repo_name, branch)
            documents.append(document)
        except Exception as e:
            logger.error(f"Failed to create document from {file_info.path}: {e}")
            failed_paths.append(file_info.path)

    logger.info(
        f"Successfully loaded {len(documents)} documents, {len(failed_paths)} failed"
    )
    return documents, failed_paths


def discover_repository_files(
    repo_url: str, branch: str = "main", file_extensions: List[str] = None
) -> Tuple[List[str], str]:
    """
    Discover files in a GitHub repository.

    Args:
        repo_url: GitHub repository URL or owner/repo format
        branch: Git branch name
        file_extensions: List of file extensions to filter

    Returns:
        Tuple of (file_paths, status_message)
    """
    if file_extensions is None:
        file_extensions = [".md", ".mdx"]

    try:
        return github_client.get_repository_tree(repo_url, branch, file_extensions)
    except Exception as e:
        logger.error(f"Failed to discover files in {repo_url}: {e}")
        return [], f"Error: {str(e)}"
