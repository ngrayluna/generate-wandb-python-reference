#!/bin/usr/python
"""
Quick and dirty Python script to post process output markdown files from lazydocs.

Note: It might be faster to create this doc using the Generator class and load in modules instead.

TO DO:
* Add source links to each class, module, etc e.g. #L123. Check note in replace_github_urls
   * Maybe add a new button? Current implementation (that was removed) is an image. Which doesn't work for us since
   we have a rule that expands images to the full width of the page. 
* Remove temp_processing function, this is a hack around not classes not being hidden
* Automate generating each module
* Add a Github action to generate the docs each time interfact.py has changes
* There are some HTML tags in the markdown that probably need to be removed...but the styling looks cool
"""
import os
import re
import argparse


def markdown_title(filename):
    """
    Create markdown title based on the filename read in.
    """
    # Not sure if this should be capitalized or not...
    base_name = os.path.basename(filename).split('.')[1].capitalize()
    return f"# {base_name}\n\n"


def replace_github_urls(text):
    """
    Add the line number to the URL for the GitHub links.
    TO DO: This does not properly fix the URL for the first top most pattern.
    """
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
    """Alphabetize the classes, etc. in the markdown file."""
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
    
    # Pattern to match H2 headings (classes)
    h2_pattern = re.compile(r'## <kbd>class</kbd> `([^`]+)`')
    
    current_section = None
    
    # Iterate over each block to find H2 headings and group content, including H3
    for block in blocks:
        h2_match = h2_pattern.search(block)
        if h2_match:
            # Extract the class name from the H2 heading
            class_name = h2_match.group(1)
            if current_section:
                sections.append(current_section)
            # Start a new section with the current block as content
            current_section = (class_name, block)
        elif current_section:
            # Append the block content to the current section
            current_section = (current_section[0], current_section[1] + block)

    # Append the last section
    if current_section:
        sections.append(current_section)

    # Sort the sections alphabetically by the class name
    sections.sort(key=lambda x: x[0])

    # Reconstruct the markdown text with the docstring followed by the sorted sections
    sorted_markdown = docstring + "\n\n" + "\n\n".join([section[1] for section in sections])

    return sorted_markdown


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
    Silly chain of processing the markdown text.
    """
    # Separating 'temp_processing' because it is a temporary fix
    markdown_text = alphabetize_headings(replace_github_urls(remove_patterns_from_markdown(fix_style(fix_imgs(markdown_text)))))

    #return alphabetize_headings(replace_github_urls(remove_patterns_from_markdown(fix_style(fix_imgs(markdown_text)))))
    return temp_processing(markdown_text)    


def rename_markdown_file(filename):
    """
    Rename markdown file. Original file name lists the entire
    module import. For example, workspaces API originally
    has a filename of `workspaces_tmp/wandb_workspaces.workspaces.interface.md`
    """
    new_filename = os.path.join(os.path.dirname(filename), os.path.basename(filename).split('.')[1]+".md")
    print(f"Renaming markdown page from {filename} to {new_filename}") 
    os.rename(filename, new_filename)


def add_import_statement():
    """Add import statement for CTAButtons component."""
    return "import { CTAButtons } from '@site/src/components/CTAButtons/CTAButtons.tsx'\n\n"


def format_CTA_button(filename, base_url="https://github.com/wandb/wandb-workspaces/tree/main"):
    """Add GitHub CTA button to the markdown file."""

    def _convert_github_md_to_py_url(url: str) -> str:
        # Define the regex pattern to match the URL and the file extension
        pattern = r"(https://github\.com/.+?/tree/main/)(.+?)\.([\w]+)$"
        
        # Replace dots in the path with slashes, change "tree" to "blob", and change ".md" to ".py"
        result = re.sub(pattern, lambda m: f"{m.group(1).replace('tree', 'blob')}{m.group(2).replace('.', '/')}.py", url)        
        return result

    href_links = _convert_github_md_to_py_url(os.path.join(base_url, os.path.basename(filename)))

    return "<CTAButtons githubLink='"+ href_links + "'/>\n\n"


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
    with open(args.file, 'r') as file:
        markdown_text = file.read()

    # Get the markdown H1 title, and get the original filename
    title = markdown_title(args.file)

    # Modify markdown content (e.g., remove <img> tags and specified comment)
    cleaned_markdown = process_text(markdown_text)

    # Create CTA button format
    github_button = format_CTA_button(args.file)

    with open(args.file, 'w') as file:
        file.write(add_import_statement())
        file.write(title)
        file.write(github_button)
        file.write(cleaned_markdown)

    # Rename markdown file name 
    rename_markdown_file(args.file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="markdown file to process")
    args = parser.parse_args()
    main(args)