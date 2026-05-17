import pytest
from doc_sync_bot.models import ChangeType
from doc_sync_bot.classifier.analyzer import DiffAnalyzer
from doc_sync_bot.github_integration.pr_linker import is_documentation_required, inject_docs_link

class MockLLMClient:
    def classify_diff(self, diff_text: str) -> ChangeType:
        return ChangeType.UNKNOWN

@pytest.fixture
def analyzer():
    return DiffAnalyzer(llm_client=MockLLMClient())

def test_pr_template_checked(analyzer):
    body = """
# Documentation
- [x] **Is documentation needed for this update?**
    """
    assert is_documentation_required(body, None, analyzer) is True

def test_pr_template_unchecked(analyzer):
    body = """
# Documentation
- [ ] **Is documentation needed for this update?**
    """
    assert is_documentation_required(body, None, analyzer) is False

def test_pr_template_missing_fallback_needed(analyzer):
    # Template checkbox is missing entirely, but we have a diff adding a new scenario
    body = "Just a simple PR description adding baremetal node scenarios"
    diff = """--- /dev/null
+++ b/scenarios/new-scenario/scenario.yaml
@@ -0,0 +1,3 @@
+name: baremetal
+description: baremetal node
+type: openshift
"""
    assert is_documentation_required(body, diff, analyzer) is True

def test_pr_template_missing_fallback_not_needed(analyzer):
    # Template checkbox missing, diff is just simple doc or README (UNKNOWN change type)
    body = "Just editing README docs"
    diff = """--- a/README.md
+++ b/README.md
@@ -1,2 +1,3 @@
 # Krkn
 # Another
+Adding simple typo fix
"""
    assert is_documentation_required(body, diff, analyzer) is False

def test_inject_docs_link_standard():
    body = """# Description
Adding awesome feature.

## Related Documentation PR (if applicable)
<-- Add the link to the corresponding documentation PR in the website repository -->
"""
    pr_url = "https://github.com/krkn-chaos/website/pull/123"
    updated = inject_docs_link(body, pr_url)
    
    assert "## Related Documentation PR (if applicable)" in updated
    assert f"- {pr_url}" in updated
    assert "<-- Add the link" not in updated

def test_inject_docs_link_fallback():
    # If the developer deleted the entire Related Documentation section
    body = """# Description
Adding awesome feature.
"""
    pr_url = "https://github.com/krkn-chaos/website/pull/123"
    updated = inject_docs_link(body, pr_url)
    
    assert "**Documentation Sync:**" in updated
    assert pr_url in updated
