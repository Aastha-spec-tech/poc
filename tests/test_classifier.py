import pytest
from doc_sync_bot.models import ChangeType
from doc_sync_bot.classifier.analyzer import DiffAnalyzer

class MockLLMClient:
    def classify_diff(self, diff_text: str) -> ChangeType:
        return ChangeType.UNKNOWN

@pytest.fixture
def analyzer():
    return DiffAnalyzer(llm_client=MockLLMClient())

def test_new_scenario_path(analyzer):
    diff = '''--- /dev/null
+++ b/scenarios/new-scenario/scenario.yaml
@@ -0,0 +1,3 @@
+name: new-scenario
+description: A new chaos scenario
+type: pod
'''
    result = analyzer.classify(diff)
    assert result.change_type == ChangeType.NEW_SCENARIO
    assert result.confidence_score == 0.85

def test_param_update_path(analyzer):
    diff = '''--- a/scenarios/pod-scenario/env.sh
+++ b/scenarios/pod-scenario/env.sh
@@ -5,2 +5,3 @@
 export TIMEOUT=300
 export EXISTING=1
+export NEW_PARAM="test"
'''
    result = analyzer.classify(diff)
    assert result.change_type == ChangeType.PARAM_UPDATE
    assert result.confidence_score == 0.85

def test_config_change_content(analyzer):
    diff = '''--- a/some/other/file.yaml
+++ b/some/other/file.yaml
@@ -10,2 +10,3 @@
   existing_config: true
   other_config: false
+  - name: new_config_field
'''
    result = analyzer.classify(diff)
    assert result.change_type == ChangeType.CONFIG_CHANGE
    assert result.confidence_score == 0.75

def test_unknown_change(analyzer):
    diff = '''--- a/README.md
+++ b/README.md
@@ -10,2 +10,3 @@
 # Krkn
 is cool
+New line here
'''
    result = analyzer.classify(diff)
    assert result.change_type == ChangeType.UNKNOWN
    assert result.confidence_score == 0.0
