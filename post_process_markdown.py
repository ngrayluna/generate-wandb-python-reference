#!/bin/usr/
"""
Quick and dirty Python script to post process output markdown files from lazydocs.

Future:
This script post processes docs spit out by using lazydocs. It might be faster
to create this doc using the Generator class and load in modules instead.
"""
import os
import re
import argparse


def markdown_title(filename):
    """
    Create markdown title based on the filename read in.
    """
    base_name = os.path.basename(filename).split('.')[1].capitalize()
    return f"# {base_name}\n\n"


def fix_imgs(text):
    """
    Taken from Weave code
    """
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
    """
    Taken from Weave code
    """    
    # The docgen produces a lot of inline styles, which are not
    # supported by the markdown parser.
    find = ' style="float:right;"'
    replace = ""
    text = text.replace(find, replace)

    return text


def replace_github_urls(text):
    """Replace the URLs in the text with the new format."""
    # Define the pattern to match the URLs
    pattern = r'(https://github\.com/wandb/wandb-workspaces)/tree/main/(.*?)/([^/]+)#L(\d+)'
    
    # Function to replace the match
    def replacer(match):
        base_url = match.group(1)
        path = match.group(2)
        # Extract just the last directory name and remove everything after it
        filename = match.group(3)
        line_number = match.group(4)
        # Construct the new URL
        return f"{base_url}/blob/main/{path}.py#L{line_number}"
    
    # Use re.sub with the replacer function
    modified_text = re.sub(pattern, replacer, text)
    
    return modified_text


def remove_patterns_from_markdown(markdown_text):
    """Remove patterns from the markdown text."""
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




def alphabetize_headings(markdown_text):
    """
    Alphabetize headings. First part of this function ensures that the module docstring is preserved.
    """
    # Split the text into two parts: the module docstring (before the first "---") and the rest
    parts = markdown_text.split('---', 1)
    
    # If there is content before the first "---", treat it as the module docstring
    if len(parts) > 1:
        docstring = parts[0].strip()  # The module docstring
        rest_of_content = '---' + parts[1]  # The remaining content starting with the first ---
    else:
        # If no separator found, assume everything is the module docstring
        docstring = markdown_text.strip()
        rest_of_content = ""
    
    # Split the rest of the content into blocks based on the "---" separator
    blocks = re.split(r'(?=---)', rest_of_content)

    sections = []
    
    # Iterate over each block to find H2 headings and group content
    for block in blocks:
        # Look for the H2 heading within the block
        match = re.search(r'## <kbd>class</kbd> `([^`]+)`', block)
        if match:
            # Extract the class name from the H2 heading
            class_name = match.group(1)
            # Store the entire block with the class name as a tuple
            sections.append((class_name, block))

    # Sort the sections alphabetically by the class name
    sections.sort(key=lambda x: x[0])

    # Reconstruct the markdown text with the docstring followed by the sorted sections
    sorted_markdown = docstring + "\n\n" + "\n\n".join([section[1] for section in sections])

    return sorted_markdown


def process_text(markdown_text):
    """
    Silly chain of processing. Clean up later
    """
    return alphabetize_headings(replace_github_urls(remove_patterns_from_markdown(fix_style(fix_imgs(markdown_text)))))


def main(args):
    with open(args.file, 'r') as file:
        markdown_text = file.read()

    # Modify the Markdown content (e.g., remove <img> tags and specified comment)
    title = markdown_title(args.file)
    cleaned_markdown = process_text(markdown_text)

    with open(args.file, 'w') as file:
        file.write(title)
        file.write(cleaned_markdown)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("file", nargs="*", help="markdown file to process")
    parser.add_argument("file", help="markdown file to process")
    args = parser.parse_args()
    main(args)