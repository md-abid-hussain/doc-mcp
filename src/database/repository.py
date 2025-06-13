"""Repository data management and statistics."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.config import settings
from ..core.types import ProcessingStatus
from .mongodb import mongodb_client

logger = logging.getLogger(__name__)


class RepositoryManager:
    """Manages repository metadata and statistics."""

    def __init__(self):
        self.repos_collection = mongodb_client.get_collection(
            settings.repos_collection_name
        )
        self.docs_collection = mongodb_client.get_collection(settings.collection_name)

    def get_available_repositories(self) -> List[str]:
        """Get list of available repositories."""
        try:
            # Use repo_name field to match existing data structure
            repos = self.repos_collection.distinct("repo_name")
            return sorted(repos) if repos else []
        except Exception as e:
            logger.error(f"Failed to get available repositories: {e}")
            return []

    def get_repository_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about all repositories."""
        try:
            repos = []
            for repo_doc in self.repos_collection.find():
                # Count documents for this repo
                repo_name = repo_doc.get("repo_name", "Unknown")
                doc_count = self.docs_collection.count_documents(
                    {"metadata.repo": repo_name}
                )

                repos.append(
                    {
                        "name": repo_name,  # Normalize to 'name' for UI consistency
                        "files": repo_doc.get(
                            "file_count", doc_count
                        ),  # Use existing file_count or count docs
                        "last_updated": repo_doc.get("last_updated", "Unknown"),
                        "status": repo_doc.get(
                            "status", "complete"
                        ),  # Default to complete for existing repos
                    }
                )

            return sorted(repos, key=lambda x: x["name"])
        except Exception as e:
            logger.error(f"Failed to get repository details: {e}")
            return []

    def get_repository_stats(self) -> Dict[str, Any]:
        """Get overall repository statistics."""
        try:
            total_repos = self.repos_collection.count_documents({})
            total_docs = self.docs_collection.count_documents({})

            # Get total files across all repos
            total_files = 0
            repos = self.repos_collection.find({}, {"file_count": 1})
            for repo in repos:
                total_files += repo.get("file_count", 0)

            # Get collection size estimates
            try:
                stats = mongodb_client.database.command(
                    "collStats", settings.collection_name
                )
                collection_size = stats.get("size", 0)
            except Exception:
                collection_size = 0

            return {
                "total_repositories": total_repos,
                "total_documents": total_docs,
                "total_files": total_files,
                "collection_size_bytes": collection_size,
                "collection_size_mb": (
                    round(collection_size / (1024 * 1024), 2)
                    if collection_size > 0
                    else 0
                ),
                "database_name": settings.db_name,
                "last_updated": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get repository stats: {e}")
            return {"error": str(e)}

    def update_repository_info(
        self, repo_name: str, file_count: int = 0, branch: Optional[str] = "main"
    ) -> bool:
        """Update repository information."""
        try:
            # Use the same structure as the working code
            self.repos_collection.replace_one(
                {"_id": repo_name},
                {
                    "_id": repo_name,
                    "repo_name": repo_name,
                    "branch": branch,  # Store branch info if needed
                    "file_count": file_count,
                    "last_updated": datetime.now(),
                    "status": ProcessingStatus.COMPLETE.value,
                },
                upsert=True,
            )
            logger.info(f"Updated repository info for: {repo_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to update repository info for {repo_name}: {e}")
            return False

    def delete_repository_data(self, repo_name: str) -> Dict[str, Any]:
        """Delete all data for a repository."""
        try:
            # Delete from documents collection
            docs_result = self.docs_collection.delete_many({"metadata.repo": repo_name})

            # Delete from repositories collection using _id (to match existing structure)
            repos_result = self.repos_collection.delete_one({"_id": repo_name})

            logger.info(
                f"Deleted repository {repo_name}: {docs_result.deleted_count} docs, {repos_result.deleted_count} repo entries"
            )

            return {
                "success": True,
                "documents_deleted": docs_result.deleted_count,
                "repository_deleted": repos_result.deleted_count > 0,
                "message": f"Successfully deleted {docs_result.deleted_count} documents for repository '{repo_name}'",
            }
        except Exception as e:
            logger.error(f"Failed to delete repository {repo_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete repository '{repo_name}': {str(e)}",
            }


# Global repository manager instance
repository_manager = RepositoryManager()
