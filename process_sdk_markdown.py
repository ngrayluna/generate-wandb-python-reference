#!/bin/usr/python
"""
Quick and dirty Python script to post process output markdown files from lazydocs.
"""
import os
import re
import argparse
import glob
from typing import List, Tuple


class MarkdownCleaner:
    """Utility class for cleaning and processing markdown files."""

    def __init__(self):
        self.patterns: List[Tuple[re.Pattern, str]] = [
            # Remove `__init__` sections
            (re.compile(r"### <kbd>method</kbd> `.*?__init__.*?```.*?```", re.DOTALL), ""),
            
            # Remove <a> tags and their content
            (re.compile(r'<a\b[^>]*>(.*?)</a>', re.DOTALL), r'\1'),
            
            # Remove module names (keep only the base module)
            (re.compile(r'(# <kbd>module</kbd> `[\w\.]+)\.[\w]+`'), r'\1`'),
            
            # Remove global variables section
            (re.compile(r"(?s)\*\*Global Variables\*\*\n[-]+\n.*?\n---"), ""),
            
            # Remove base class links and headers
            (re.compile(r'<a href="[^"]*">\s*<img[^>]*>\s*</a>\s*## <kbd>class</kbd> `Base`'), ""),
            
            # Replace bold tags with plain text
            (re.compile(r'<b>(.*?)</b>'), r'\1'),
            
            # Remove footer generated by lazydocs
            (re.compile(r'---\n+_This file was automatically generated via \[lazydocs\]\([^\)]+\)\._\n*'), ""),

            # Convert h4 titles (####) to h3 titles (###)
            (re.compile(r'####\s*'), r'### '),
        ]

    def clean_text(self, markdown_text: str) -> str:
        """Apply all cleaning patterns to the given markdown text."""
        cleaned_text = markdown_text
        for pattern, replacement in self.patterns:
            cleaned_text = pattern.sub(replacement, cleaned_text)
        return cleaned_text        


def process_text(markdown_text: str) -> str:
    """Process markdown text using the MarkdownCleaner utility."""
    cleaner = MarkdownCleaner()
    return cleaner.clean_text(markdown_text)
        

def main(args):

    for filename in glob.glob(os.path.join(os.getcwd(), args.output_directory , '*.md')):
        print(f"Reading in {filename} for processing...")
        # Read markdown content from file
        with open(filename, 'r') as file:
            markdown_text = file.read()
            
        # Modify markdown content (e.g., remove <img> tags and specified comment)
        cleaned_markdown = process_text(markdown_text)

        # Write cleaned markdown content back to file
        with open(filename, 'w') as file:
            file.write(cleaned_markdown)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_directory", default="wandb_sdk_docs", help="directory where the markdown files to process exist")
    args = parser.parse_args()
    main(args)
