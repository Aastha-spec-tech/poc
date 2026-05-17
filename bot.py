import os
import sys

# Ensure doc_sync_bot is importable if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from doc_sync_bot.classifier.analyzer import DiffAnalyzer
from doc_sync_bot.models import ChangeType
from doc_sync_bot.llm_generator.generator import LLMGenerator
from doc_sync_bot.llm_generator.client import LLMClient

def main():
    print("Starting Krkn-Chaos Documentation Sync Bot...")
    
    # POC Demonstration Diff
    diff_text = '''--- a/scenarios/kubelet-density/env.sh
+++ b/scenarios/kubelet-density/env.sh
@@ -5,2 +5,3 @@
 export KUBELET_DENSITY_TIMEOUT=300
+export NEW_METRIC_FLAG="true"'''
    
    # Initialize LLM Client and Generator
    llm_client = LLMClient() # Requires OPENAI_API_KEY
    generator = LLMGenerator(client=llm_client)
    
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
    
    # Phase 3 will introduce GitHub integration
    print("Phase 2 LLM Integration completed successfully.")

if __name__ == "__main__":
    main()
