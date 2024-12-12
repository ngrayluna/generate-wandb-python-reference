#! /bin/usr/python
import os
import re
import inspect

import lazydocs

###### TEMP USE LOCAL VERSION OF WANDB for debugging ######
import sys
import pydantic
from pathlib import Path
# Path to the local version of the `wandb` package
local_wandb_path = Path("/Users/noahluna/Documents/GitHub/wandb")

# Add the local package path to sys.path
sys.path.insert(0, str(local_wandb_path))

# Confirm the correct version of wandb is being used
import wandb
print("Using wandb from:", wandb.__file__)
###### TEMP END ######


def get_api_list_from_pyi(file_path):
    """Get list of public APIs from a .pyi file. Exclude APIs marked with # doc:exclude.

    Args:
        file_path (str): Path to the .pyi file.
    """
    # Debug variables
    raw_content = ""
    matched_all_content = ""

    # Adjusted regex to match `__all__` with more flexible spacing and comments
    all_pattern = re.compile(r'__all__\s*=\s*\((.*?)\)', re.DOTALL)
    # Regex to extract individual items
    item_pattern = re.compile(r'"(.*?)"')
    # Regex to detect # doc:exclude
    exclude_pattern = re.compile(r'#\s*doc:exclude')

    try:
        with open(file_path, "r") as f:
            raw_content = f.read()  # Read file content
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

    # Match `__all__` section
    match = all_pattern.search(raw_content)
    if match:
        matched_all_content = match.group(1)
        print("Matched __all__ content:\n", matched_all_content)
    else:
        print("__all__ definition not found!")
        return []

    # Process the matched content line by line
    filtered_items = []
    for line in matched_all_content.splitlines():
        if exclude_pattern.search(line):
            continue  # Skip lines with # doc:exclude
        item_match = item_pattern.search(line)
        if item_match:
            filtered_items.append(item_match.group(1))

    return filtered_items

def add_frontmatter(filename):
    """Add frontmatter to the markdown file."""
    base_name = os.path.basename(filename).split('.')[0]
    return f"---\ntitle: {base_name}\n---\n\n"

def _github_button(href_links):
    """To do: Add hugo scripting to add this function. For now, just add code line # for debugging."""
    # return f"{{< github_button href={href_links} >}}"+ "\n\n"
    return "{{< github_button href=" + href_links + " >}}"+ "\n\n"    

def format_github_button(filename, base_url="https://github.com/wandb/wandb/blob/main/wandb"):
    """Add GitHub button to the markdown file."""

    def _extract_filename_from_path(path: str) -> str:
        # Only get path after "wandb/" in the URL
        _, _, wandb_path = path.partition("wandb/")
        return wandb_path

    href_links = os.path.join(base_url, _extract_filename_from_path(filename))
    return _github_button(href_links)

def create_class_markdown(obj, module, generator, filename):
    with open(filename, 'w') as file:
        file.write(add_frontmatter(filename))
        file.write(format_github_button(inspect.getfile(obj)))        
        file.write("\n\n")
        # file.write( 'source code line ' +  str(inspect.getsourcelines(obj)[1])) # In the future, add this to the markdown file
        file.write(generator.class2md(obj))

def create_function_markdown(obj, module, generator, filename):
    with open(filename, 'w') as file:
        file.write(add_frontmatter(filename))
        file.write(format_github_button(inspect.getfile(obj)))
        file.write("\n\n")
        # file.write( 'source code line ' +  str(inspect.getsourcelines(obj)[1])) # In the future, add this to the markdown file
        file.write(generator.func2md(obj))

def _check_temp_dir():
    # Check if temporary directory exists
    if not os.path.exists('sdk_docs_temp/'):
        os.makedirs('sdk_docs_temp/')

def get_output_markdown_path(api_list_item):
    # Store generated files in sdk_docs_temp directory
    # This directory is used by process_sdk_markdown.py
    _check_temp_dir()

    filename = api_list_item + '.md'
    return os.path.join(os.getcwd(), 'sdk_docs_temp/', filename)


def create_markdown(api_list_item, module, src_base_url):
    # Create output filepath
    filename = get_output_markdown_path(api_list_item)

    # Get object from module
    obj = getattr(module, api_list_item)
    
    # Get generator object
    generator = lazydocs.MarkdownGenerator(src_base_url=src_base_url)

    # Check if object is a class or function
    if str(type(obj)) == "<class 'type'>":
        print(f"Generating docs for {obj} class", str(type(obj)))
        create_class_markdown(obj, module, generator, filename=filename)
    elif str(type(obj)) == "<class 'function'>":
        print(f"Generating docs for {obj} function", str(type(obj)))
        create_function_markdown(obj, module, generator, filename=filename)
    else:
        print(f"Skipping {obj}", str(type(obj)))   


def main():
    module = wandb
    src_base_url = "https://github.com/wandb/wandb/tree/main/"
    
    # Get list of public APIs
    api_list = get_api_list_from_pyi("/Users/noahluna/Documents/GitHub/wandb/wandb/__init__.pyi")

    # To do: Get api_list from module
    for api in api_list:
        create_markdown(api, module, src_base_url)

if __name__  == "__main__":
    main()