from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class ChangeType(Enum):
    NEW_SCENARIO = "NEW_SCENARIO"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    CLI_FLAG = "CLI_FLAG"
    PARAM_UPDATE = "PARAM_UPDATE"
    UNKNOWN = "UNKNOWN"

@dataclass
class PRContext:
    repo_name: str
    pr_number: int
    diff_text: str
    diff_url: str

@dataclass
class ClassificationResult:
    change_type: ChangeType
    affected_files: List[str]
    confidence_score: float
