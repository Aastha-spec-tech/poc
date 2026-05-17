import re
from typing import List, Tuple
from doc_sync_bot.models import ChangeType

# Rule definitions for path-based classification
# Format: List of (regex pattern, change_type)
PATH_RULES: List[Tuple[re.Pattern, ChangeType]] = [
    (re.compile(r"^scenarios/.*?/.*?\.yaml$"), ChangeType.NEW_SCENARIO),
    (re.compile(r"^scenarios/.*?/env\.sh$"), ChangeType.PARAM_UPDATE),
    (re.compile(r"^cmd/.*?\.go$"), ChangeType.CLI_FLAG),
    (re.compile(r"^config/.*?\.yaml$"), ChangeType.CONFIG_CHANGE),
]

# Rule definitions for content-based classification
# Format: List of (regex pattern, change_type)
CONTENT_RULES: List[Tuple[re.Pattern, ChangeType]] = [
    (re.compile(r"^export\s+([A-Z_]+)="), ChangeType.PARAM_UPDATE), # Added ENV var
    (re.compile(r"^\s*-\s*name:\s*['\"]?([a-zA-Z0-9_-]+)['\"]?"), ChangeType.CONFIG_CHANGE), # Added config field
]
