import re
from doc_sync_bot.models import ChangeType

# Regex to check if the checkbox is marked (- [x] or - [X])
CHECKBOX_PATTERN = re.compile(r"-\s*\[[xX]\]\s*\*\*Is\s+documentation\s+needed\s+for\s+this\s+update\?\*\*")
# Regex to check if the checkbox is present at all (even if unmarked)
CHECKBOX_PRESENT_PATTERN = re.compile(r"-\s*\[\s*\]\s*\*\*Is\s+documentation\s+needed\s+for\s+this\s+update\?\*\*")

RELATED_PR_HEADER = "## Related Documentation PR (if applicable)"

def is_documentation_required(pr_body: str, diff_text: str = None, analyzer = None) -> bool:
    """
    Determines if documentation is required for this PR.
    1. First tries to parse the PR template checkbox.
    2. If the template is present, strictly adheres to the checkbox value.
    3. If the template is completely missing/altered, falls back to using the DiffAnalyzer 
       to determine if the changes are documentable.
    """
    pr_body = pr_body or ""
    
    # Check if checkbox template exists (either checked or unchecked)
    has_checked = bool(CHECKBOX_PATTERN.search(pr_body))
    has_unchecked = bool(CHECKBOX_PRESENT_PATTERN.search(pr_body))
    
    if has_checked or has_unchecked:
        print("PR template checkbox detected.")
        return has_checked
        
    # Fallback Mode: Template is completely missing/edited
    print("WARNING: PR template checkbox not found in description. Falling back to diff analysis...")
    if diff_text and analyzer:
        classification = analyzer.classify(diff_text)
        # If classifier detects any known change type that is NOT unknown, we require docs
        if classification.change_type != ChangeType.UNKNOWN:
            print(f"Fallback Classification success: {classification.change_type.value}. Docs required.")
            return True
            
    print("Fallback Classification: No documentable changes detected. Docs NOT required.")
    return False

def inject_docs_link(pr_body: str, website_pr_url: str) -> str:
    """
    Injects the website PR link into the original PR description under the 
    '## Related Documentation PR (if applicable)' header.
    If the header is missing, appends the link beautifully to the end of the PR body.
    """
    pr_body = pr_body or ""
    link_markdown = f"- {website_pr_url}"
    
    if RELATED_PR_HEADER in pr_body:
        # Match the header and any surrounding whitespace, template comments
        # Format: ## Related Documentation PR (if applicable)\n<-- Add the link... -->
        # We replace the placeholder comment or whatever is immediately below the header
        pattern = re.escape(RELATED_PR_HEADER) + r"(\s*)(<--[\s\S]*?-->)?"
        replacement = f"{RELATED_PR_HEADER}\n{link_markdown}"
        
        updated_body = re.sub(pattern, replacement, pr_body)
        return updated_body
    else:
        # Fallback: Header was deleted, append link to the bottom
        print("WARNING: 'Related Documentation PR' section not found. Appending link to the bottom of the description.")
        separator = "\n\n---\n"
        append_text = f"**Documentation Sync:** Automatically opened website draft PR: {website_pr_url}"
        return f"{pr_body}{separator}{append_text}"
