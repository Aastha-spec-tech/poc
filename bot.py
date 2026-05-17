import os
import sys

# Ensure doc_sync_bot is importable if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doc_sync_bot.classifier.analyzer import DiffAnalyzer
from doc_sync_bot.models import ChangeType

def main():
    print("Starting Krkn-Chaos Documentation Sync Bot...")
    
    # 1. Dummy diff for POC refactoring demonstration
    diff_text = '''--- a/scenarios/kubelet-density/env.sh
+++ b/scenarios/kubelet-density/env.sh
@@ -5,2 +5,3 @@
 export KUBELET_DENSITY_TIMEOUT=300
+export NEW_METRIC_FLAG="true"'''
    
    print("1. Initializing Analyzer...")
    # Mock LLM Client for Stage 3 fallback
    class MockLLM:
        def classify_diff(self, diff_text):
            return ChangeType.UNKNOWN
            
    analyzer = DiffAnalyzer(llm_client=MockLLM())
    
    print("2. Classifying Change...")
    result = analyzer.classify(diff_text)
    
    print(f"Result:")
    print(f"  Change Type: {result.change_type.value}")
    print(f"  Confidence:  {result.confidence_score}")
    print(f"  Files:       {result.affected_files}")
    
    # Phase 2 will introduce LLM generators here
    # Phase 3 will introduce GitHub integration
    print("Phase 1 modular structure set up successfully.")

if __name__ == "__main__":
    main()
