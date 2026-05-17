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
        print(f"Target Repository: Aastha-spec-tech/krkn-website")
        print(f"Target Branch:     docs-sync/pr-123-krkn-hub")
        print(f"Target File:       {target_doc_path}")
        print(f"Commit Message:    docs: Auto-sync from krkn-hub PR #123")
        
        mock_website_pr_url = "https://github.com/Aastha-spec-tech/krkn-website/pull/999"
        
        # Test backlink injection
        print("\n=== DRY RUN PR LINKING (EDIT ORIGINAL PR) ===")
        updated_pr_body = inject_docs_link(pr_body_mock, mock_website_pr_url)
        print("Updated Original PR Body:")
        print(updated_pr_body)
        print("=============================================")
        
        # Test refinement loop
        print("\n=== DRY RUN PR COMMENT REFINEMENT LOOP (CHATBOT) ===")
        mock_comment = "@docs-bot please change the default timeout to 500 and add a warning note that it only works on AWS."
        print(f"User Comment: {mock_comment}")
        
        feedback = mock_comment.replace("@docs-bot", "").strip()
        refined_doc_mock = generator.client.refine_documentation(updated_doc, feedback)
        print("\n=== REFINED DOC (UPDATED BY BOT) ===")
        print(refined_doc_mock)
        print("=====================================")
        
        reply_body_mock = (
            f"### Documentation Refinement Successful!\n\n"
            f"I've updated the documentation based on your feedback: *\"{feedback}\"*\n"
            f"The changes have been pushed directly to your PR branch.\n\n"
            f"<!-- docs-sync-bot -->\n"
            f"<!-- Refined comment ID: 999123 -->"
        )
        print("Bot Comment Response:")
        print(reply_body_mock)
        print("====================================================")
        print("Dry run complete. Configure GitHub App credentials to execute real PR creation.")
    else:
        # Trigger real GitHub App branch/PR creation
        try:
            pr_url = pr_creator.create_draft_pr(
                website_repo_name="Aastha-spec-tech/krkn-website",
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
            
            # Start Live Refinement Polling for comments on the newly created PR
            print("Checking for new reviews and feedback comments on the PR...")
            from doc_sync_bot.github_integration.refinement import process_pr_refinements
            branch_name = f"docs-sync/pr-123-krkn-hub"
            process_pr_refinements(
                gh_client=gh_client,
                repo_name="Aastha-spec-tech/krkn-website",
                pr_number=999, # In reality, we'd extract the PR number from pr_url
                file_path=target_doc_path,
                branch_name=branch_name,
                llm_client=llm_client
            )
        except Exception as e:
            print(f"Failed to execute GitHub App PR lifecycle: {e}")
            
    print("GitHub App & Metadata PR Sync completed successfully.")

if __name__ == "__main__":
    main()
