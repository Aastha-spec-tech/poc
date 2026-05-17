import pytest
from unittest.mock import MagicMock
from doc_sync_bot.models import ChangeType
from doc_sync_bot.github_integration.refinement import process_pr_refinements
from doc_sync_bot.llm_generator.client import LLMClient

class MockLLMClient:
    def refine_documentation(self, existing_doc: str, feedback: str) -> str:
        return f"{existing_doc}\nREFINED:{feedback}"

def test_process_pr_refinements_trigger():
    # Setup mocks
    gh_client_mock = MagicMock()
    repo_mock = MagicMock()
    pr_mock = MagicMock()
    
    gh_client_mock.g = MagicMock()
    gh_client_mock.g.get_repo.return_value = repo_mock
    repo_mock.get_pull.return_value = pr_mock
    
    # Mock issue comments
    comment_1 = MagicMock()
    comment_1.body = "@docs-bot change the timeout to 500"
    comment_1.id = 111
    
    pr_mock.get_issue_comments.return_value = [comment_1]
    
    # Mock repository file retrieval
    file_contents_mock = MagicMock()
    file_contents_mock.decoded_content = b"title: Test Doc"
    file_contents_mock.sha = "1234abcd"
    repo_mock.get_contents.return_value = file_contents_mock
    
    # Execute loop
    llm_client = MockLLMClient()
    processed = process_pr_refinements(
        gh_client=gh_client_mock,
        repo_name="Aastha-spec-tech/krkn-website",
        pr_number=999,
        file_path="docs/test.md",
        branch_name="docs-sync/pr-test",
        llm_client=llm_client
    )
    
    # Assert comment was processed
    assert len(processed) == 1
    assert processed[0] == (111, "change the timeout to 500")
    
    # Verify commit was pushed to GitHub branch
    repo_mock.update_file.assert_called_once_with(
        path="docs/test.md",
        message="docs: Refined based on PR comment review #111",
        content="title: Test Doc\nREFINED:change the timeout to 500",
        sha="1234abcd",
        branch="docs-sync/pr-test"
    )
    
    # Verify bot commented back to user
    pr_mock.create_issue_comment.assert_called_once()
    reply_body = pr_mock.create_issue_comment.call_args[0][0]
    assert "### Documentation Refinement Successful!" in reply_body
    assert "change the timeout to 500" in reply_body
    assert "<!-- Refined comment ID: 111 -->" in reply_body

def test_process_pr_refinements_already_replied():
    # If the bot has already replied to this comment, it should skip it.
    gh_client_mock = MagicMock()
    repo_mock = MagicMock()
    pr_mock = MagicMock()
    
    gh_client_mock.g = MagicMock()
    gh_client_mock.g.get_repo.return_value = repo_mock
    repo_mock.get_pull.return_value = pr_mock
    
    # Original user comment
    comment_1 = MagicMock()
    comment_1.body = "@docs-bot change the timeout to 500"
    comment_1.id = 111
    
    # Previous bot reply (contains signature and comment marker)
    comment_2 = MagicMock()
    comment_2.body = "### Documentation Refinement Successful!\n<!-- docs-sync-bot -->\n<!-- Refined comment ID: 111 -->"
    comment_2.id = 112
    
    pr_mock.get_issue_comments.return_value = [comment_1, comment_2]
    
    llm_client = MockLLMClient()
    processed = process_pr_refinements(
        gh_client=gh_client_mock,
        repo_name="Aastha-spec-tech/krkn-website",
        pr_number=999,
        file_path="docs/test.md",
        branch_name="docs-sync/pr-test",
        llm_client=llm_client
    )
    
    # Assert comment was skipped since bot already responded
    assert len(processed) == 0
    repo_mock.update_file.assert_not_called()
    pr_mock.create_issue_comment.assert_not_called()
