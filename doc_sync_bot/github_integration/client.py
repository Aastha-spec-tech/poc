import os
import requests
from github import Github, GithubIntegration
from doc_sync_bot.models import PRContext

class GitHubClientWrapper:
    def __init__(self, app_id: int = None, private_key: str = None, installation_id: int = None):
        """
        Initializes the GitHub client using GitHub App Authentication.
        """
        # Read from arguments or environment
        self.app_id = app_id or os.getenv("GITHUB_APP_ID")
        self.private_key = private_key or os.getenv("GITHUB_PRIVATE_KEY")
        self.installation_id = installation_id or os.getenv("GITHUB_INSTALLATION_ID")
        
        self.g = None
        self.token = None
        
        if self.app_id and self.private_key and self.installation_id:
            try:
                # Handle escaped newlines if private key is supplied as a single env string
                formatted_key = self.private_key.replace(r'\n', '\n')
                
                # Setup GitHub Integration
                integration = GithubIntegration(
                    integration_id=int(self.app_id),
                    private_key=formatted_key
                )
                
                # Authenticate as the specific installation of the App
                auth = integration.get_auth(int(self.installation_id))
                self.token = auth.token
                self.g = Github(auth=auth)
                print("GitHub App Authentication initialized successfully.")
            except Exception as e:
                print(f"Failed to authenticate as GitHub App: {e}")
                self.g = None
                self.token = None
        else:
            print("WARNING: GitHub App credentials (ID, private key, or installation ID) not configured.")
            print("Operating in MOCK/DRY-RUN mode.")

    def fetch_pr_context(self, repo_name: str, pr_number: int) -> PRContext:
        """Fetches the PR details and diff URL, then downloads the diff using the installation token."""
        if not self.g or not self.token:
            raise ValueError("GitHub Client is not authenticated. Please set GitHub App credentials.")
            
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
            
    def edit_pr_description(self, repo_name: str, pr_number: int, new_body: str) -> bool:
        """Edits the description (body) of a PR in the code repository."""
        if not self.g:
            raise ValueError("GitHub Client is not authenticated.")
        try:
            repo = self.g.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            pr.edit(body=new_body)
            print(f"Successfully updated PR #{pr_number} description.")
            return True
        except Exception as e:
            print(f"Failed to edit PR description: {e}")
            return False
