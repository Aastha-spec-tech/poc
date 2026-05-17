import os
import sys

# Ensure doc_sync_bot is importable if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doc_sync_bot.classifier.analyzer import DiffAnalyzer
from doc_sync_bot.models import ChangeType
from doc_sync_bot.llm_generator.generator import LLMGenerator
from doc_sync_bot.llm_generator.client import LLMClient
from doc_sync_bot.github_integration.client import GitHubClientWrapper
from doc_sync_bot.github_integration.pr_creator import PRCreator
from doc_sync_bot.github_integration.pr_linker import is_documentation_required, inject_docs_link

def main():
    print("Starting Krkn-Chaos Documentation Sync Bot...")
    
    # POC Demonstration Diff
    diff_text = '''--- a/scenarios/kubelet-density/env.sh
+++ b/scenarios/kubelet-density/env.sh
@@ -5,2 +5,3 @@
 export KUBELET_DENSITY_TIMEOUT=300
 export EXISTING=1
+export NEW_METRIC_FLAG="true"'''
    
    # Initialize GitHub App and LLM Clients
    app_id = os.getenv("GITHUB_APP_ID")
    private_key = os.getenv("GITHUB_PRIVATE_KEY")
    installation_id = os.getenv("GITHUB_INSTALLATION_ID")
    
    is_dry_run = not (app_id and private_key and installation_id)
    
    print(f"Running in {'DRY RUN' if is_dry_run else 'PRODUCTION'} mode.")
    
    llm_client = LLMClient() if not is_dry_run else None # In production, set OPENAI_API_KEY
    generator = LLMGenerator(client=llm_client)
    gh_client = GitHubClientWrapper(app_id=app_id, private_key=private_key, installation_id=installation_id)
    pr_creator = PRCreator(github_client=gh_client)
    
    # POC Mock PR Body (Simulating PR Template is filled)
    pr_body_mock = """# Type of change
- [ ] Refactor
- [x] New feature

# Description
Adding a new node action Baremetal scenario.

# Documentation
- [x] **Is documentation needed for this update?**

If checked, a documentation PR must be created in the website repository.

## Related Documentation PR (if applicable)
<-- Add the link to the corresponding documentation PR in the website repository -->
"""

    print("1. Initializing Analyzer...")
    analyzer = DiffAnalyzer(llm_client=llm_client)
    
    print("2. Stage 0 Gating: Checking if documentation is required...")
    # Check if doc is required using template checkbox or fallback diff parsing
    docs_needed = is_documentation_required(pr_body_mock, diff_text, analyzer)
    if not docs_needed:
        print("Gatekeeping: Documentation sync is NOT required for this PR. Exiting.")
        return
        
    print("3. Classifying Change...")
    result = analyzer.classify(diff_text)
    
    print(f"Result:")
    print(f"  Change Type: {result.change_type.value}")
    print(f"  Confidence:  {result.confidence_score}")
    print(f"  Files:       {result.affected_files}")
    
    print("4. Generating Documentation...")
    existing_doc_mock = "---\ntitle: Kubelet Density\n---\n| Parameter | Type | Default | Description |\n|---|---|---|---|\n| KUBELET_DENSITY_TIMEOUT | int | 300 | Timeout |"
    updated_doc = generator.generate_and_validate(result.change_type, diff_text, existing_doc_mock)
    
    print("\n=== GENERATED DOC ===")
    print(updated_doc)
    print("=====================")
    
    print("5. Creating Website PR...")
    target_doc_path = "content/en/docs/scenarios/kubelet-density.md"
    
    if is_dry_run:
        print("\n=== DRY RUN PR CREATION ===")
        print(f"Target Repository: krkn-chaos/website")
        print(f"Target Branch:     docs-sync/pr-123-krkn-hub")
        print(f"Target File:       {target_doc_path}")
        print(f"Commit Message:    docs: Auto-sync from krkn-hub PR #123")
        
        mock_website_pr_url = "https://github.com/krkn-chaos/website/pull/999"
        
        # Test backlink injection
        print("\n=== DRY RUN PR LINKING (EDIT ORIGINAL PR) ===")
        updated_pr_body = inject_docs_link(pr_body_mock, mock_website_pr_url)
        print("Updated Original PR Body:")
        print(updated_pr_body)
        print("=============================================")
        print("Dry run complete. Configure GitHub App credentials to execute real PR creation.")
    else:
        # Trigger real GitHub App branch/PR creation
        try:
            pr_url = pr_creator.create_draft_pr(
                website_repo_name="krkn-chaos/website",
                target_file_path=target_doc_path,
                updated_content=updated_doc,
                change_type=result.change_type,
                original_repo="krkn-hub",
                original_pr_number=123
            )
            print(f"PR Successfully Created: {pr_url}")
            
            # Link it back by editing original PR
            gh_client.edit_pr_description(
                repo_name="krkn-hub",
                pr_number=123,
                new_body=inject_docs_link(pr_body_mock, pr_url)
            )
        except Exception as e:
            print(f"Failed to execute GitHub App PR lifecycle: {e}")
            
    print("GitHub App & Metadata PR Sync completed successfully.")

if __name__ == "__main__":
    main()
