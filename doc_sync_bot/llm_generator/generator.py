from doc_sync_bot.models import ChangeType
from doc_sync_bot.llm_generator.client import LLMClient
from doc_sync_bot.llm_generator.validators import validate_markdown

class LLMGenerator:
    def __init__(self, client: LLMClient = None):
        self.client = client or LLMClient()
        
    def generate_and_validate(self, change_type: ChangeType, diff_text: str, existing_doc: str = "") -> str:
        """
        Generates documentation and runs it through the validation pipeline.
        If validation fails, we could retry (not implemented in POC) or fallback.
        """
        print(f"Generating docs for {change_type.value}...")
        updated_content = self.client.generate_documentation(change_type, diff_text, existing_doc)
        
        print("Validating output...")
        
        # If the change is just updating a table, the LLM might only return the table snippet.
        # If it's a NEW_SCENARIO, it returns a full file.
        # We should only strictly validate frontmatter for NEW_SCENARIO.
        if change_type == ChangeType.NEW_SCENARIO:
            is_valid, err = validate_markdown(updated_content)
            if not is_valid:
                print(f"WARNING: Validation failed: {err}")
                # In production, we'd trigger a retry loop with the LLM here.
                # For the POC, we'll append an HTML comment flag
                updated_content += f"\n<!-- DOC-SYNC-BOT WARNING: Validation Failed: {err} -->"
        
        return updated_content
