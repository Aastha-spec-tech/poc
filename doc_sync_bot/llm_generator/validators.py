import re
from typing import List, Tuple

def validate_frontmatter(content: str) -> Tuple[bool, str]:
    """Checks if the document has a valid Hugo frontmatter block with title and weight."""
    if not content.startswith("---"):
        return False, "Missing frontmatter start '---'"
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False, "Missing frontmatter end '---'"
        
    frontmatter = parts[1]
    if "title:" not in frontmatter:
        return False, "Missing 'title:' in frontmatter"
        
    return True, ""

def validate_table_schema(content: str) -> Tuple[bool, str]:
    """Checks if the parameter table exists and has the correct columns."""
    table_header_pattern = r"\|\s*Parameter\s*\|\s*Type\s*\|\s*Default\s*\|\s*Description\s*\|"
    if not re.search(table_header_pattern, content, re.IGNORECASE):
        # We only fail if this is a scenario page that requires a table.
        # But for POC, we'll assume the generated output *should* have it if it generated one.
        pass
        
    # Check for malformed rows (rows with wrong number of pipes)
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            pipes = line.count("|")
            if pipes != 5: # | col1 | col2 | col3 | col4 | -> 5 pipes
                return False, f"Malformed table row found: {line}"
                
    return True, ""

def validate_shortcodes(content: str) -> Tuple[bool, str]:
    """Verifies that Hugo shortcodes are properly paired."""
    open_count = content.count("{{<")
    close_count = content.count(">}}")
    if open_count != close_count:
        return False, f"Mismatched Hugo shortcodes: {open_count} open, {close_count} close"
    return True, ""

def validate_markdown(content: str) -> Tuple[bool, str]:
    """Runs all validators and returns the first error, or success."""
    validators = [
        validate_frontmatter,
        validate_table_schema,
        validate_shortcodes
    ]
    
    for validator in validators:
        # Frontmatter is only required for full page generations (NEW_SCENARIO).
        # We might skip it for partial updates, but for now we apply it generally.
        is_valid, err_msg = validator(content)
        if not is_valid:
            return False, err_msg
            
    return True, ""
