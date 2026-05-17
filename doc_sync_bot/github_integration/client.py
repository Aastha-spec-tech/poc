import os
import requests
from github import Github
from doc_sync_bot.models import PRContext

class GitHubClientWrapper:
    def __init__(self, token: str = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            # We don't crash immediately so it can run mock modes
            print("WARNING: GITHUB_TOKEN environment variable not set.")
        self.g = Github(self.token) if self.token else None

    def fetch_pr_context(self, repo_name: str, pr_number: int) -> PRContext:
        """Fetches the PR details and diff URL, then downloads the diff."""
        if not self.g:
            raise ValueError("GitHub Client is not authenticated. Please set GITHUB_TOKEN.")
            
        repo = self.g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        diff_url = pr.diff_url
        response = requests.get(diff_url, headers={"Authorization": f"token {self.token}"})
        if response.status_code == 200:
            return PRContext(
                repo_name=repo_name,
                pr_number=pr_number,
                diff_text=response.text,
                diff_url=diff_url
            )
        else:
            raise Exception(f"Failed to fetch PR diff: status code {response.status_code}")

    def fetch_existing_doc(self, website_repo_name: str, file_path: str) -> str:
        """Fetches existing markdown file content from the website repo."""
        if not self.g:
            raise ValueError("GitHub Client is not authenticated.")
            
        website_repo = self.g.get_repo(website_repo_name)
        try:
            file_content = website_repo.get_contents(file_path)
            return file_content.decoded_content.decode('utf-8')
        except Exception:
            print(f"File not found in website repo: {file_path}. Assuming new page.")
            return ""
