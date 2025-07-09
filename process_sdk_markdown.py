#!/usr/bin/env python
"""
Enhanced script to remove entire classes, methods, functions, optionally `__init__`
methods, **and individual attribute bullets** flagged with
    <!-- lazydoc-ignore-class-attributes -->
from lazydocs‑generated markdown.
"""
import os
import re
import argparse
import glob
from typing import List, Tuple


class MarkdownCleaner:
    # ------------------------------------------------------------------ #
    def __init__(self):
        # 1) simple one‑off replacements
        self.patterns: List[Tuple[re.Pattern, str]] = [
            (re.compile(r'<a\b[^>]*>(.*?)</a>', re.DOTALL), r'\1'),
            (re.compile(r'(# <kbd>module</kbd> `[\w\.]+)\.[\w]+`'), r'\1`'),
            (re.compile(
                r"\*\*Global Variables\*\*\n[-]+\n(?:(?!## |# <kbd>)[\s\S])*\n",
                re.MULTILINE
            ), ""),
            (re.compile(r'<b>(.*?)</b>'), r'\1'),
            (re.compile(
                r'---\n+_This file was automatically generated via '
                r'\[lazydocs\]\([^)]+\)._\n*'
            ), ""),
            (re.compile(r'####\s*'), r'### '),
        ]

        # 2) existing large‑block patterns
        self.block_pattern = re.compile(
            r"(?s)(## <kbd>class</kbd> `.*?`|"
            r"### <kbd>(?:method|function)</kbd> `.*?`\n\n```python\n.*?\n```\n\n.*?|"
            r"### <kbd>property</kbd> .*?\n\n.*?)(?=\n## |\n### |\Z)"
        )
        self.class_pattern = re.compile(r"(?s)## <kbd>class</kbd> `.*?`.*?(?=\n## <kbd>class</kbd>|$)")
        self.function_pattern = re.compile(r"(?s)## <kbd>function</kbd> `.*?`\n\n```python\n.*?\n```\n\n.*?(?=\n## |\Z)")
        self.init_pattern = re.compile(
            r"(?s)<!-- lazydoc-ignore-init: internal -->\s*"
            r"### <kbd>method</kbd> `.*?__init__.*?`\n\n```python\n.*?\n```\n\n.*?(?=\n## |\n### |\Z)"
        )
        self.classmethod_pattern = re.compile(
            r"(?s)### <kbd>classmethod</kbd> `.*?`\n\n```python\n.*?\n```\n\n.*?(?=\n## |\n### |\Z)"
        )

        # 3) what a single attribute bullet‑block looks like
        self.attr_block_pattern = re.compile(
            r"(?sm)^( {0,3}- .*?)"            # top‑level bullet start …
            r"(?=\n {0,3}- |\n## |\n### |\Z)" # … up to next bullet/header/EOF
        )

    # ------------------------------------------------------------------ #
    def clean_text(self, markdown_text: str) -> str:
        cleaned = markdown_text

        # -- simple substitutions
        for pat, repl in self.patterns:
            cleaned = pat.sub(repl, cleaned)

        # -- your original ignore markers
        cleaned = self._remove_ignored_blocks(cleaned, "<!-- lazydoc-ignore: internal -->",     self.block_pattern)
        cleaned = self._remove_ignored_blocks(cleaned, "<!-- lazydoc-ignore-class: internal -->", self.class_pattern)
        cleaned = self._remove_ignored_blocks(cleaned, "<!-- lazydoc-ignore-function: internal -->", self.function_pattern)
        cleaned = self._remove_ignored_blocks(cleaned, "<!-- lazydoc-ignore-classmethod: internal -->", self.classmethod_pattern)
        cleaned = self.init_pattern.sub("", cleaned)

        # -- NEW: attribute bullets flagged with the inline literal
        cleaned = self._remove_ignored_blocks(
            cleaned,
            "<!-- lazydoc-ignore-class-attributes -->",
            self.attr_block_pattern
        )

        return cleaned

    # ------------------------------------------------------------------ #
    def _remove_ignored_blocks(self, text: str, token: str, pattern: re.Pattern) -> str:
        """Drop any regex‑matched block that contains the given token."""
        def keep_or_drop(match: re.Match) -> str:
            return "" if token in match.group(0) else match.group(0)
        return pattern.sub(keep_or_drop, text)


# ----------------------------------------------------------------------#
def process_text(markdown_text: str) -> str:
    return MarkdownCleaner().clean_text(markdown_text)


def main(args):
    for filename in glob.glob(os.path.join(os.getcwd(), args.output_directory, "*.md")):
        with open(filename, "r") as f:
            text = f.read()
        with open(filename, "w") as f:
            f.write(process_text(text))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post‑process lazydocs markdown.")
    parser.add_argument("--output_directory", default="wandb_sdk_docs",
                        help="Directory containing markdown files to process")
    main(parser.parse_args())
