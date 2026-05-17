import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from doc_sync_bot.models import ChangeType
from doc_sync_bot.llm_generator.prompts import SYSTEM_PROMPT, CLASSIFIER_PROMPT, GENERATOR_PROMPTS

class LLMClient:
    def __init__(self):
        # We default to ChatOpenAI for the POC. Ensure OPENAI_API_KEY is in env.
        # Alternatively, this can be swapped out for ChatAnthropic or ChatGoogleGenerativeAI
        self.llm = ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo")
        
    def classify_diff(self, diff_text: str) -> ChangeType:
        """Stage 3 fallback: Classify an ambiguous diff using the LLM."""
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
