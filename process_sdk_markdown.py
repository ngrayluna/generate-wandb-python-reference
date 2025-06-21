#!/usr/bin/env python
"""
Enhanced script to remove entire classes, methods, functions, and optionally `__init__` methods
from lazydocs-generated markdown based on custom ignore comments.
"""
import os
import re
import argparse
import glob
from typing import List, Tuple


class MarkdownCleaner:
    def __init__(self):
        self.patterns: List[Tuple[re.Pattern, str]] = [
            (re.compile(r'<a\b[^>]*>(.*?)</a>', re.DOTALL), r'\1'),
            (re.compile(r'(# <kbd>module</kbd> `[\w\.]+)\.[\w]+`'), r'\1`'),
            (re.compile(r"\*\*Global Variables\*\*\n[-]+\n(?:(?!## |# <kbd>)[\s\S])*\n", re.MULTILINE), ""),
            (re.compile(r'<b>(.*?)</b>'), r'\1'),
            (re.compile(r'---\n+_This file was automatically generated via \[lazydocs\]\([^\)]+\)._\n*'), ""),
            (re.compile(r'####\s*'), r'### '),
        ]

        self.block_pattern = re.compile(
            r"(?s)(## <kbd>class</kbd> `.*?`|"
            r"### <kbd>(?:method|function)</kbd> `.*?`\n\n```python\n.*?\n```\n\n.*?|"
            r"### <kbd>property</kbd> .*?\n\n.*?)(?=\n## |\n### |\Z)"
        )

        self.class_pattern = re.compile(
            r"(?s)## <kbd>class</kbd> `.*?`.*?(?=\n## <kbd>class</kbd>|$)"
        )

        self.function_pattern = re.compile(
            r"(?s)## <kbd>function</kbd> `.*?`\n\n```python\n.*?\n```\n\n.*?(?=\n## |\Z)"
        )

        self.init_pattern = re.compile(
            r"(?s)<!-- lazydoc-ignore-init: internal -->\s*"
            r"### <kbd>method</kbd> `.*?__init__.*?`\n\n```python\n.*?\n```\n\n.*?(?=\n## |\n### |\Z)"
        )

        self.classmethod_pattern = re.compile(
            r"(?s)### <kbd>classmethod</kbd> `.*?`\n\n```python\n.*?\n```\n\n.*?(?=\n## |\n### |\Z)"
        )        

    def clean_text(self, markdown_text: str) -> str:
        cleaned_text = markdown_text
        for pattern, replacement in self.patterns:
            cleaned_text = pattern.sub(replacement, cleaned_text)

        cleaned_text = self.remove_ignored_blocks(
            cleaned_text, "<!-- lazydoc-ignore: internal -->", self.block_pattern
        )

        cleaned_text = self.remove_ignored_blocks(
            cleaned_text, "<!-- lazydoc-ignore-class: internal -->", self.class_pattern
        )

        cleaned_text = self.remove_ignored_blocks(
            cleaned_text, "<!-- lazydoc-ignore-function: internal -->", self.function_pattern
        )

        cleaned_text = self.remove_ignored_blocks(
            cleaned_text, "<!-- lazydoc-ignore-classmethod: internal -->", self.classmethod_pattern
)

        cleaned_text = self.init_pattern.sub("", cleaned_text)

        return cleaned_text

    def remove_ignored_blocks(self, markdown_text: str, ignore_str: str, pattern: re.Pattern) -> str:
        def filter_block(match: re.Match) -> str:
            return "" if ignore_str in match.group(0) else match.group(0)

        return pattern.sub(filter_block, markdown_text)


def process_text(markdown_text: str) -> str:
    cleaner = MarkdownCleaner()
    return cleaner.clean_text(markdown_text)


def main(args):
    for filename in glob.glob(os.path.join(os.getcwd(), args.output_directory, '*.md')):
        with open(filename, 'r') as file:
            markdown_text = file.read()

        cleaned_markdown = process_text(markdown_text)

        with open(filename, 'w') as file:
            file.write(cleaned_markdown)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_directory",
        default="wandb_sdk_docs",
        help="directory containing markdown files to process"
    )
    args = parser.parse_args()
    main(args)
