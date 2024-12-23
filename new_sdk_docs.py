#!/bin/usr/python
import os
import re
import inspect

from lazydocs import MarkdownGenerator

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

class DocodileMaker:
    def __init__(self, module, api, output_dir):
        self.module = module
        self.api_item = api
        self.output_dir = output_dir
        self._object_attribute = None
        self._object_type = None
        self._file_path = None
        self._filename = None

    def _ensure_object_attribute(self):
        """Ensure `_object_attribute` is initialized."""
        if self._object_attribute is None:
            self._object_attribute = getattr(self.module, self.api_item)
            self._update_object_type()
            self._update_file_path()
            self._update_filename()

    def _update_object_type(self):
        """Determine the type of the object."""
        attr_type = str(type(self._object_attribute))
        if attr_type == "<class 'type'>":
            self._object_type = "class"
        elif attr_type == "<class 'function'>":
            self._object_type = "function"
        else:
            self._object_type = "other"

    def _update_file_path(self):
        """Determine the file path of the object."""
        try:
            self._file_path = inspect.getfile(self._object_attribute)
        except TypeError:
            self._file_path = None  # Handle cases where `inspect.getfile()` fails.

    def _update_filename(self):
        """Determine the filename of the object."""
        self._filename = os.path.join(os.getcwd(), self.output_dir, self.api_item + ".md")  

    @property
    def object_attribute_value(self):
        self._ensure_object_attribute()
        return self._object_attribute

    @property
    def object_type(self):
        self._ensure_object_attribute()
        return self._object_type

    @property
    def getfile_path(self):
        self._ensure_object_attribute()
        print("File path:", self._file_path)
        # if self._file_path is None:
        #     raise ValueError("File path is not available for the specified object.")
        return self._file_path
    
    @property
    def filename(self):
        self._ensure_object_attribute()
        return self._filename


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
    """Add frontmatter to the markdown file.
    
    Args:
        filename (str): Name of the file.
    """
    base_name = os.path.basename(filename).split('.')[0]
    return f"---\ntitle: {base_name}\n---\n\n"

def _github_button(href_links):
    """To do: Add hugo scripting to add this function. For now, just add code line # for debugging.
    
    Args:
        href_links (str): URL for the GitHub button.
    """
    return "{{< github_button href=" + href_links + " >}}"+ "\n\n"    

def format_github_button(filename, base_url="https://github.com/wandb/wandb/blob/main/wandb"):
    """Add GitHub button to the markdown file.
    
    Args:
        filename (str): Name of the file.
        base_url (str): Base URL for the GitHub button.
    """
    def _extract_filename_from_path(path: str) -> str:
        # Only get path after "wandb/" in the URL
        _, _, wandb_path = path.partition("wandb/")
        return wandb_path

    href_links = os.path.join(base_url, _extract_filename_from_path(filename))
    return _github_button(href_links)

def create_markdown(docodile, generator):
    """Create markdown file for the API.
    
    Args:
        docodile (DocodileMaker): Docodile object.
        generator (MarkdownGenerator): Markdown generator object.
        filename (str): Name of the file.
    """
    print("Opening file:", docodile.filename)

    with open(docodile.filename, 'w') as file:
        file.write(add_frontmatter(docodile.filename))
        file.write(format_github_button(docodile.getfile_path))
        file.write("\n\n")

        if docodile.object_type == "class":
            print("Creating class markdown", "\n\n")
            file.write(generator.class2md(docodile.object_attribute_value))
        elif docodile.object_type == "function":
            print("Creating function markdown", "\n\n")
            file.write(generator.func2md(docodile.object_attribute_value))
        else:
            print("No doc generator for this object type")


def check_temp_dir(temp_output_dir):
    """Check if temporary directory exists."""
    if not os.path.exists(temp_output_dir):
        os.makedirs(temp_output_dir)


def main():
    module = wandb
    src_base_url = "https://github.com/wandb/wandb/tree/main/"
    temp_output_dir = "new_sdk_docs_temp"
    valid_object_types = ["class", "function"]

    # Check if temporary directory exists
    check_temp_dir(temp_output_dir)

    # Create MarkdownGenerator object. We use the same generator for all APIs.
    generator = MarkdownGenerator(src_base_url=src_base_url)

    # Get list of public APIs
    api_list = get_api_list_from_pyi("/Users/noahluna/Documents/GitHub/wandb/wandb/__init__.pyi")

    # Get list of public APIs from a .pyi file. Exclude APIs marked with # doc:exclude.
    for api_list_item in api_list:

        # Create Docodile object
        docodile = DocodileMaker(module, api_list_item, temp_output_dir)

        if docodile.object_type in valid_object_types:
            # Create markdown file for the API
            create_markdown(docodile, generator)


    # Generate overview markdown
    # with open(os.path.join(os.getcwd(), 'sdk_docs_temp/', "README.md"), 'w') as file:
    #     file.write(generator.overview2md())

if __name__  == "__main__":
    main()
