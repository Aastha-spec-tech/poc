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

def main():
    print("Starting Krkn-Chaos Documentation Sync Bot...")
    
    # POC Demonstration Diff
    diff_text = '''--- a/scenarios/kubelet-density/env.sh
+++ b/scenarios/kubelet-density/env.sh
@@ -5,2 +5,3 @@
 export KUBELET_DENSITY_TIMEOUT=300
 export EXISTING=1
+export NEW_METRIC_FLAG="true"'''
    
    # Initialize GitHub and LLM Clients
    github_token = os.getenv("GITHUB_TOKEN")
    
    # Mode configurations
    is_dry_run = not github_token
    
    print(f"Running in {'DRY RUN' if is_dry_run else 'PRODUCTION'} mode.")
    
    llm_client = LLMClient() if not is_dry_run else None # In production, set OPENAI_API_KEY
    generator = LLMGenerator(client=llm_client)
    gh_client = GitHubClientWrapper(token=github_token)
    pr_creator = PRCreator(github_client=gh_client)
    
    print("1. Initializing Analyzer...")
    analyzer = DiffAnalyzer(llm_client=llm_client)
    
    print("2. Classifying Change...")
    result = analyzer.classify(diff_text)
    
    print(f"Result:")
    print(f"  Change Type: {result.change_type.value}")
    print(f"  Confidence:  {result.confidence_score}")
    print(f"  Files:       {result.affected_files}")
    
    print("3. Generating Documentation...")
    existing_doc_mock = "---\ntitle: Kubelet Density\n---\n| Parameter | Type | Default | Description |\n|---|---|---|---|\n| KUBELET_DENSITY_TIMEOUT | int | 300 | Timeout |"
    updated_doc = generator.generate_and_validate(result.change_type, diff_text, existing_doc_mock)
    
    print("\n=== GENERATED DOC ===")
    print(updated_doc)
    print("=====================")
    
    print("4. Creating Website PR...")
    target_doc_path = "content/en/docs/scenarios/kubelet-density.md"
    
    if is_dry_run:
        print("\n=== DRY RUN PR CREATION ===")
        print(f"Target Repository: krkn-chaos/website")
        print(f"Target Branch:     docs-sync/pr-123-krkn-hub")
        print(f"Target File:       {target_doc_path}")
        print(f"Commit Message:    docs: Auto-sync from krkn-hub PR #123")
        print("PR Description:")
        
        checklist = pr_creator.get_checklist(result.change_type) if hasattr(pr_creator, 'get_checklist') else "Review checklists initialized."
        print(f"  - Title: Kubelet Density Update")
        print(f"  - Change Type: {result.change_type.value}")
        print("Dry run complete. Set GITHUB_TOKEN to execute real PR creation.")
    else:
        # Trigger real Github API branch/PR creation
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
        except Exception as e:
            print(f"Failed to create PR via API: {e}")
            
    print("Phase 3 GitHub PR Integration completed successfully.")

if __name__ == "__main__":
    main()
