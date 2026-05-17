from unidiff import PatchSet
from typing import List, Tuple
from doc_sync_bot.models import ChangeType, ClassificationResult
from doc_sync_bot.classifier.rules import PATH_RULES, CONTENT_RULES

class DiffAnalyzer:
    def __init__(self, llm_client=None):
        """
        Initializes the DiffAnalyzer.
        :param llm_client: A client interface for the fallback LLM classification (Stage 3).
        """
        self.llm_client = llm_client

    def classify(self, diff_text: str) -> ClassificationResult:
        """
        Executes the 3-stage classification pipeline on a unified diff.
        """
        patch_set = PatchSet(diff_text)
        
        if not patch_set:
            return ClassificationResult(ChangeType.UNKNOWN, [], 0.0)
            
        affected_files = [patched_file.path for patched_file in patch_set]
        
        # Stage 1: Path Rules
        path_type = self._apply_path_rules(patch_set)
        if path_type != ChangeType.UNKNOWN:
            return ClassificationResult(path_type, affected_files, 0.85)
            
        # Stage 2: Content Rules
        content_type = self._apply_content_rules(patch_set)
        if content_type != ChangeType.UNKNOWN:
            return ClassificationResult(content_type, affected_files, 0.75)
            
        # Stage 3: LLM Fallback (if client provided)
        if self.llm_client:
            llm_type = self._apply_llm_fallback(diff_text)
            if llm_type != ChangeType.UNKNOWN:
                return ClassificationResult(llm_type, affected_files, 0.60)
                
        return ClassificationResult(ChangeType.UNKNOWN, affected_files, 0.0)
        
    def _apply_path_rules(self, patch_set: PatchSet) -> ChangeType:
        """Stage 1: Classify based on file paths."""
        for patched_file in patch_set:
            path = patched_file.path
            for pattern, change_type in PATH_RULES:
                if pattern.search(path):
                    if change_type == ChangeType.NEW_SCENARIO and not patched_file.is_added_file:
                        continue # NEW_SCENARIO implies an added file
                    return change_type
        return ChangeType.UNKNOWN
        
    def _apply_content_rules(self, patch_set: PatchSet) -> ChangeType:
        """Stage 2: Classify based on diff hunks content."""
        for patched_file in patch_set:
            for hunk in patched_file:
                for line in hunk:
                    if line.is_added:
                        for pattern, change_type in CONTENT_RULES:
                            if pattern.search(line.value):
                                return change_type
        return ChangeType.UNKNOWN
        
    def _apply_llm_fallback(self, diff_text: str) -> ChangeType:
        """Stage 3: Use LLM to classify ambiguous diffs."""
        # This will be implemented when we wire up LangChain/OpenAI
        # For now, it delegates to the mock client or returns UNKNOWN
        return self.llm_client.classify_diff(diff_text) if hasattr(self.llm_client, 'classify_diff') else ChangeType.UNKNOWN
