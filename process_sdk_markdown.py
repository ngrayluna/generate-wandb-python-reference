#!/bin/usr/python
"""
Quick and dirty Python script to post process output markdown files from lazydocs.

Note: It might be faster to create this doc using the Generator class and load in modules instead.

TO DO:
* Add source links to each class, module, etc e.g. #L123. Check note in replace_github_urls
* Remove temp_processing function, this is a hack around not classes not being hidden
* There are some HTML tags in the markdown that probably need to be removed...but the styling looks cool
"""
import os
import re
import argparse
import glob

def remote_init_sections(markdown_text):
    raw_pattern = r"### <kbd>method</kbd> `.*?__init__.*?```.*?```" # Match `__init__` sections
    init_pattern = re.compile(raw_pattern, re.DOTALL)
    return init_pattern.sub("", markdown_text)


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

    # Remove `__init__` sections
    cleaned_text = remote_init_sections(cleaned_text)

    return cleaned_text



def temp_processing(content, internal_tag="INTERNAL"):
    """
    Remove classes that contain the term 'INTERNAl' in their docstring.
    This is a temporary fix while we wait to hide these classes.
    """
    #Keyword to look for in the class docstring
    internal_tag = "INTERNAL"
    
    # Pattern to match class definitions and their content
    # The pattern matches from '## <kbd>class</kbd>' to the next markdown header or the end of the file
    class_pattern = re.compile(r"(## <kbd>class</kbd> .+?)(?=## <kbd>class</kbd>|$)", re.DOTALL)
    
    # Pattern to match all <a></a> tags and their content
    a_tag_pattern = re.compile(r'<a\b[^>]*>(.*?)</a>', re.DOTALL)
    
    # 1. Remove sections that contain the internal tag
    matches = class_pattern.findall(content)
    for match in matches:
        if internal_tag in match:
            content = content.replace(match, "")
    
    #2. Remove all <a></a> tags
    content = re.sub(a_tag_pattern, '', content)

    return content 


def process_text(markdown_text):
    """
    Silly chain of processing the markdown text. Clean up later.
    """

    # Separating 'temp_processing' because it is a temporary fix
    markdown_text = remove_patterns_from_markdown(fix_style(fix_imgs(markdown_text)))
    return temp_processing(markdown_text)   



## The following functions are taken from Weave API Docs ## 

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


def main(args):

    for filename in glob.glob(os.path.join(os.getcwd(), args.output_directory , '*.md')):

        print(f"Reading in {filename} for processing...")

        with open(filename, 'r') as file:
            markdown_text = file.read()

        # Modify markdown content (e.g., remove <img> tags and specified comment)
        cleaned_markdown = process_text(markdown_text)

        with open(filename, 'w') as file:
            file.write(cleaned_markdown)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_directory", default="sdk_docs_temp", help="markdown file to process")
    args = parser.parse_args()
    main(args)
