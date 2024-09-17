#!/bin/usr/
import os
import re
import argparse


def markdown_title(filename):
    base_name = os.path.basename(filename).split('.')[1].capitalize()
    return f"# {base_name}\n\n"


def fix_imgs(text):
    # Images (used for source code tags) are not closed. While many
    # html parsers handle this, the markdown parser does not. This
    # function fixes that.
    # Example:
    # <img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square">
    # becomes
    # <img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" />

    # This regex matches the img tag and captures the attributes
    # and the src attribute.
    pattern = r'<img(.*?)(src=".*?")>'

    # This function replaces the match with the same match, but with
    # a closing slash before the closing bracket.
    def replace_with_slash(match):
        return f"<img{match.group(1)}{match.group(2)} />"

    # Replace all occurrences of the pattern with the function
    text = re.sub(pattern, replace_with_slash, text)

    return text

def fix_style(text):
    # The docgen produces a lot of inline styles, which are not
    # supported by the markdown parser.
    find = ' style="float:right;"'
    replace = ""
    text = text.replace(find, replace)

    return text



def process_text(markdown_text):
    return remove_patterns_from_markdown(fix_style(fix_imgs(markdown_text)))


def remove_patterns_from_markdown(markdown_text):
    module_name_pattern = r'(# <kbd>module</kbd> `[\w\.]+)\.[\w]+`'
    global_variable_pattern = r"(?s)\*\*Global Variables\*\*\n[-]+\n.*?\n---"
    base_class_pattern = r'<a href="[^"]*">\s*<img[^>]*>\s*</a>\s*## <kbd>class</kbd> `Base`'
    bold_tags_pattern = r'<b>(.*?)</b>'
    footer_pattern = r'---\n+_This file was automatically generated via \[lazydocs\]\([^\)]+\)\._\n*'

    cleaned_text = re.sub(module_name_pattern, r'\1`', markdown_text)
    cleaned_text = re.sub(global_variable_pattern, '', cleaned_text).strip()
    cleaned_text = re.sub(base_class_pattern, '', cleaned_text).strip()
    cleaned_text = re.sub(bold_tags_pattern, r'\1', cleaned_text)
    cleaned_text = re.sub(footer_pattern, '', cleaned_text).strip()

    return cleaned_text



def main(args):
    with open(args.file, 'r') as file:
        markdown_text = file.read()


    title = markdown_title(args.file)
    
    

    # Modify the Markdown content (e.g., remove <img> tags and specified comment)
    cleaned_markdown = process_text(markdown_text)

    with open(args.file, 'w') as file:
        file.write(title)
        file.write(cleaned_markdown)

    return



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("file", nargs="*", help="markdown file to process")
    parser.add_argument("file", help="markdown file to process")
    args = parser.parse_args()
    main(args)