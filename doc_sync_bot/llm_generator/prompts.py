from doc_sync_bot.models import ChangeType

SYSTEM_PROMPT = """You are a technical documentation writer for krkn-chaos, a Kubernetes chaos
engineering framework. You write Hugo/Docsy Markdown following exact existing conventions."""

CLASSIFIER_PROMPT = """You are an expert system analyzing a pull request diff.
Classify the following diff into ONE of the following categories:
- NEW_SCENARIO: A completely new chaos scenario directory and files were added.
- CONFIG_CHANGE: A field was added to an existing YAML configuration.
- CLI_FLAG: A new flag was added to a cobra command (e.g. in cmd/).
- PARAM_UPDATE: A new environment variable was added (e.g. in env.sh).
- UNKNOWN: The change does not fit any of the above categories.

Respond with ONLY the category name.

DIFF:
{diff_text}
"""

GENERATOR_PROMPTS = {
    ChangeType.PARAM_UPDATE: """A PR was merged that adds/modifies environment variables.
Look at the provided DIFF and the EXISTING DOC.
Add a new row to the parameter table for the new variable, or update the existing row.
Output ONLY the updated parameter table section. Do not output the whole document.
Make sure the table format matches exactly: | Parameter | Type | Default | Description |

DIFF:
{diff_text}

EXISTING DOC:
{existing_doc}
""",
    
    ChangeType.NEW_SCENARIO: """A PR was merged that adds a completely new scenario.
Look at the provided DIFF which contains the new scenario structure (usually a YAML or env.sh).
Generate a complete Hugo/Docsy Markdown page for this new scenario.
It MUST include Frontmatter (title, weight, description).
It MUST include a parameters table.

DIFF:
{diff_text}
""",

    ChangeType.CONFIG_CHANGE: """A PR was merged that modifies a YAML configuration.
Look at the provided DIFF and the EXISTING DOC.
Add the new configuration field to the existing parameter table.
Output ONLY the updated parameter table section.

DIFF:
{diff_text}

EXISTING DOC:
{existing_doc}
""",

    ChangeType.CLI_FLAG: """A PR was merged that adds a new CLI flag.
Look at the provided DIFF and the EXISTING DOC.
Add the new flag to the existing CLI flags reference section.
Output ONLY the updated flags section.

DIFF:
{diff_text}

EXISTING DOC:
{existing_doc}
"""
}

REFINEMENT_PROMPT = """You are a documentation refinement agent for krkn-chaos.
You are given the EXISTING DOC and a USER FEEDBACK comment.
Rewrite the EXISTING DOC to satisfy the USER FEEDBACK.
Preserve all formatting, frontmatter, and standard table structures unless explicitly asked to modify them.
Output ONLY the complete updated documentation content in Markdown format.

EXISTING DOC:
{existing_doc}

USER FEEDBACK:
{feedback}
"""
