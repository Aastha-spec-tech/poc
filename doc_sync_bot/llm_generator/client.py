import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from doc_sync_bot.models import ChangeType
from doc_sync_bot.llm_generator.prompts import SYSTEM_PROMPT, CLASSIFIER_PROMPT, GENERATOR_PROMPTS, REFINEMENT_PROMPT

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.llm = ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo", openai_api_key=self.api_key)
        else:
            self.llm = None
            print("WARNING: OPENAI_API_KEY not found. LLMClient operating in MOCK/DRY-RUN mode.")
        
    def classify_diff(self, diff_text: str) -> ChangeType:
        """Stage 3 fallback: Classify an ambiguous diff using the LLM."""
        if not self.llm:
            return ChangeType.UNKNOWN
            
        prompt = CLASSIFIER_PROMPT.format(diff_text=diff_text)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages).content.strip()
        
        try:
            return ChangeType(response)
        except ValueError:
            return ChangeType.UNKNOWN

    def generate_documentation(self, change_type: ChangeType, diff_text: str, existing_doc: str = "") -> str:
        """Generate the updated markdown content based on the change type."""
        if not self.llm:
            # Return a beautiful mock generation for demonstration purposes
            return f"{existing_doc}\n\n<!-- Mocked LLM Sync Update for {change_type.value} -->\n| NEW_METRIC_FLAG | bool | true | New metric flag added via LFX POC |"
            
        if change_type not in GENERATOR_PROMPTS:
            return existing_doc
            
        prompt = GENERATOR_PROMPTS[change_type].format(
            diff_text=diff_text,
            existing_doc=existing_doc
        )
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages).content.strip()
        return response

    def refine_documentation(self, existing_doc: str, feedback: str) -> str:
        """Stage 4 interactive loop: Refine generated documentation using comments as feedback."""
        if not self.llm:
            # Return a beautiful mock refinement for demonstration purposes
            return f"{existing_doc}\n\n<!-- Mocked LLM Refinement based on: {feedback} -->\n**WARNING:** Baremetal scenarios should only be run on fully verified IPMI nodes."
            
        prompt = REFINEMENT_PROMPT.format(
            existing_doc=existing_doc,
            feedback=feedback
        )
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages).content.strip()
        return response
