"""GitHub URL and repository parsing utilities."""

from typing import Tuple
from urllib.parse import urlparse

from ..core.exceptions import GitHubError


def parse_github_url(url: str) -> Tuple[str, str]:
    """
    Parse GitHub URL to extract owner and repository name.

    Args:
        url: GitHub URL in various formats, including:
            - https://github.com/owner/repo
            - github.com/owner/repo
            - owner/repo (without the domain part)

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        GitHubError: If URL format is invalid
    """
    if not url or not url.strip():
        raise GitHubError("Empty URL provided")

    url = url.strip().rstrip("/")  # Remove trailing slashes

    # If the URL doesn't start with "http" or "github.com", assume it's in "owner/repo" format
    if not url.startswith(("https://github.com", "github.com")):
        url = "https://github.com/" + url

    # Use urlparse to parse the URL
    parsed_url = urlparse(url)

    # Extract the path (which is typically in the form /owner/repo)
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) == 2:
        owner, repo = path_parts
        return owner, repo
    else:
        raise GitHubError(f"Invalid GitHub URL format: {url}")


def build_github_api_url(
    owner: str, repo: str, path: str = "", branch: str = "main"
) -> str:
    """
    Build GitHub API URL for repository operations.

    Args:
        owner: Repository owner
        repo: Repository name
        path: Optional path within repository
        branch: Branch name (default: main)

    Returns:
        Formatted GitHub API URL
    """
    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    if path:
        return f"{base_url}/contents/{path.strip('/')}?ref={branch}"
    else:
        return f"{base_url}/git/trees/{branch}?recursive=1"


def build_github_web_url(
    owner: str, repo: str, path: str = "", branch: str = "main"
) -> str:
    """
    Build GitHub web URL for files.

    Args:
        owner: Repository owner
        repo: Repository name
        path: Optional path within repository
        branch: Branch name (default: main)

    Returns:
        Formatted GitHub web URL
    """
    base_url = f"https://github.com/{owner}/{repo}"

    if path:
        return f"{base_url}/blob/{branch}/{path}"
    else:
        return f"{base_url}/tree/{branch}"


def is_valid_github_repo_format(repo_string: str) -> bool:
    """
    Check if string is in valid GitHub repo format.

    Args:
        repo_string: String to validate

    Returns:
        True if valid format, False otherwise
    """
    try:
        parse_github_url(repo_string)
        return True
    except GitHubError:
        return False
