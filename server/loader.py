from typing import Dict, Iterator, List, Literal, Optional
from langchain_community.document_loaders.github import BaseGitHubLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_core.documents import Document
import requests
import re

class GitHubPRLoader(BaseGitHubLoader):
    """Load pull requests of a GitHub repository."""

    state: Optional[Literal["open", "closed", "all"]] = None
    """Filter on PR state. Can be one of: 'open', 'closed', 'all'."""
    sort: Optional[Literal["created", "updated", "popularity", "long-running"]] = None
    """What to sort results by. Can be one of: 'created', 'updated', 'popularity', 'long-running'."""
    direction: Optional[Literal["asc", "desc"]] = None
    """The direction to sort the results by. Can be one of: 'asc', 'desc'."""
    head: Optional[str] = None
    """Filter by the head branch name."""
    base: Optional[str] = None
    """Filter by the base branch name."""
    page: Optional[int] = None
    """The page number for paginated results. 
        Defaults to 1 in the GitHub API."""
    per_page: Optional[int] = None
    """Number of items per page. 
        Defaults to 30 in the GitHub API."""

    def lazy_load(self) -> Iterator[Document]:
        """
        Get pull requests of a GitHub repository.

        Returns:
            A list of Documents with attributes:
                - page_content
                - metadata
                    - url
                    - title
                    - creator
                    - created_at
                    - updated_at
                    - closed_at
                    - merged_at
                    - number of comments
                    - state
                    - labels
                    - assignee
                    - milestone
                    - locked
                    - number
                    - is_pull_request
                    - head
                    - base
        """
        url: Optional[str] = self.url
        while url:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            prs = response.json()
            for pr in prs:
                doc = self.parse_pr(pr)
                yield doc
            if (
                response.links
                and response.links.get("next")
                and (not self.page and not self.per_page)
            ):
                url = response.links["next"]["url"]
            else:
                url = None

    def parse_pr(self, pr: dict) -> Document:
        """Create Document objects from a list of GitHub pull requests."""
        metadata = {
            "url": pr["html_url"],
            "title": pr["title"],
            "creator": pr["user"]["login"],
            "created_at": pr["created_at"],
            "updated_at": pr["updated_at"],
            "closed_at": pr["closed_at"],
            "merged_at": pr["merged_at"],
            "comments": pr["comments_url"],
            "state": pr["state"],
            "labels": [label["name"] for label in pr["labels"]],
            "assignee": pr["assignee"]["login"] if pr["assignee"] else None,
            "milestone": pr["milestone"]["title"] if pr["milestone"] else None,
            "locked": pr["locked"],
            "number": pr["number"],
            "head": pr["head"]["ref"],
            "base": pr["base"]["ref"],
        }
        content = pr["body"] if pr["body"] is not None else ""
        return Document(page_content=content, metadata=metadata)

    @property
    def query_params(self) -> str:
        """Create query parameters for GitHub API."""
        query_params_dict = {
            "state": self.state,
            "sort": self.sort,
            "direction": self.direction,
            "head": self.head,
            "base": self.base,
            "page": self.page,
            "per_page": self.per_page,
        }
        query_params_list = [
            f"{k}={v}" for k, v in query_params_dict.items() if v is not None
        ]
        query_params = "&".join(query_params_list)
        return query_params

    @property
    def url(self) -> str:
        """Create URL for GitHub API."""
        return f"{self.github_api_url}/repos/{self.repo}/pulls?{self.query_params}"
    
    def get_changed_files(self, pull_number: int) -> List[Dict]:
        """
        Get the changed files in a specific pull request.

        Args:
            pull_number: The number of the pull request.

        Returns:
            A list of dictionaries, each containing information about a changed file.
        """
        url = f"{self.github_api_url}/repos/{self.repo}/pulls/{pull_number}/files"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

def extract_info(pr_link):
    # Define the regex pattern to capture the repository path and the PR number
    pattern = r'https:\/\/github\.com\/([^\/]+\/[^\/]+)\/pull\/(\d+)'
    
    # Use re.search to find the match
    match = re.search(pattern, pr_link)
    
    if match:
        repo_path = match.group(1)
        pr_number = match.group(2)
        return repo_path, pr_number
    else:
        return None, None
