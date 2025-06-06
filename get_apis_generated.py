"""Extract API signatures from markdown files in a directory and save them to a text file."""

import os
import re

def extract_object_type(text):
    """Extract the object_type from the frontmatter block (between ---)."""
    frontmatter_match = re.search(r'^---(.*?)---', text, re.DOTALL | re.MULTILINE)
    if not frontmatter_match:
        return "Unknown"

    frontmatter = frontmatter_match.group(1)
    object_type_match = re.search(r'object_type\s*:\s*([^\n]+)', frontmatter)
    return object_type_match.group(1).strip() if object_type_match else "Unknown"

def extract_api_signatures(text):
    """
    Extract all markdown API signature headers like:
    ## <kbd>class</kbd> `Artifact`
    ### <kbd>method</kbd> `Artifact.__init__`
    ### <kbd>property</kbd> Artifact.aliases
    """
    # Match lines like: ## <kbd>class</kbd> `Artifact`
    pattern_code = re.compile(
        r'^\s*#+\s*<kbd>([^<]+)</kbd>\s+`([^`]+)`', re.MULTILINE
    )

    # Match lines like: ### <kbd>property</kbd> Artifact.aliases (no backticks)
    pattern_plain = re.compile(
        r'^\s*#+\s*<kbd>([^<]+)</kbd>\s+([^\s`][\w\.\_]+)', re.MULTILINE
    )

    matches = []
    for match in pattern_code.finditer(text):
        api_type = match.group(1).strip().lower()
        api_name = match.group(2).strip()
        matches.append((api_type, api_name))

    for match in pattern_plain.finditer(text):
        api_type = match.group(1).strip().lower()
        api_name = match.group(2).strip()
        matches.append((api_type, api_name))

    return matches

def collect_all_api_entries(input_dir, output_file):
    all_entries = []

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(".md"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                object_type = extract_object_type(text)
                signatures = extract_api_signatures(text)

                for api_type, api_name in signatures:
                    entry = f"{api_type} {api_name}    [object_type: {object_type}]"
                    all_entries.append(entry)

    # Deduplicate and sort
    unique_sorted_entries = sorted(set(all_entries))

    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in unique_sorted_entries:
            f.write(entry + '\n')

# Example usage:
input_markdown_dir = "python-library/"            # Set this to your markdown folder
output_api_list_file = "all_apis.txt"   # The result file
collect_all_api_entries(input_markdown_dir, output_api_list_file)
