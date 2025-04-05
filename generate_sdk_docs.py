#!/bin/usr/python

import os
import re
import inspect
import argparse
import importlib  # make sure this is at the top

# import wandb
from lazydocs import MarkdownGenerator
from typing import List

###### USE LOCAL VERSION OF WANDB for debugging ######
import sys
from pathlib import Path

# Path to the local version of the `wandb` package
local_wandb_path = Path("/Users/noahluna/Documents/GitHub/wandb")

# Add the local package path to sys.path
sys.path.insert(0, str(local_wandb_path))

# Confirm the correct version of wandb is being used
import wandb
print("Using wandb from:", wandb.__file__)
###### END ######

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
        if (self._object_attribute is None) and (hasattr(self.module, self.api_item)):
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
        elif attr_type == "<class 'module'>":
            self._object_type = "module"
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
        # if self._file_path is None:
        #     raise ValueError("File path is not available for the specified object.")
        return self._file_path
    
    @property
    def filename(self):
        self._ensure_object_attribute()
        return self._filename


def _title_key_string(docodile):
    base_name = os.path.basename(docodile.filename).split('.')[0]
    return f"title: {base_name}\n"

def _type_key_string(docodile):
    """Determine the type of the object and return the appropriate frontmatter string."""
    if "sdk" and "data_type" in docodile.getfile_path:
        return "object_type: data_type\n"
    elif "apis" and "public" in docodile.getfile_path:
        return "object_type: public_apis_namespace\n"
    elif "launch" in docodile.getfile_path:
        return "object_type: launch_apis_namespace\n"
    else:
        return "object_type: api\n"

def add_frontmatter(docodile):
    """Add frontmatter to the markdown file.
    
    Args:
        filename (str): Name of the file.
    """
    return "---\n" + _title_key_string(docodile) + _type_key_string(docodile) + "---\n\n"


def _github_button(href_links):
    """To do: Add hugo scripting to add this function. For now, just add code line # for debugging.
    
    Args:
        href_links (str): URL for the GitHub button.
    """
    return "{{< cta-button githubLink=" + href_links + " >}}"+ "\n\n"


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
        file.write(add_frontmatter(docodile))
        file.write(format_github_button(docodile.getfile_path))
        file.write("\n\n")

        if docodile.object_type == "class":
            print("Creating class markdown", "\n\n")
            file.write(generator.class2md(docodile.object_attribute_value))
        elif docodile.object_type == "function":
            print("Creating function markdown", "\n\n")
            file.write(generator.func2md(docodile.object_attribute_value))
        elif docodile.object_type == "module":
            print("Creating module markdown", "\n\n")
            file.write(generator.module2md(docodile.object_attribute_value))
        else:
            print("No doc generator for this object type")


def check_temp_dir(temp_output_dir):
    """Check if temporary directory exists.
    
    Args:
        temp_output_dir (str): Name of the temporary output directory.
    """
    if not os.path.exists(temp_output_dir):
        os.makedirs(temp_output_dir)

def get_public_apis_from_init(file_path: str) -> List[str]:
    """Extracts module names from an __init__.py file in the wandb.apis.public namespace.
    
    Args:
        file_path (str): Path to the __init__.py file.

    Returns:
        List[str]: List of module names with ".md" suffix.
    """
    modules = set()
    pattern = re.compile(r"^from wandb\.apis\.public\.(\w+) import")

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = pattern.match(line)
            if match:
                modules.add(match.group(1))

    # Convert to sorted list and append ".md" to each module name
    return sorted(modules)

def get_api_list_from_init(file_path):
    """Get list of APIs from a Python __init__.py or .pyi file.
    Excludes APIs marked with # doc:exclude.

    Args:
        file_path (str): Path to the file.

    Returns:
        list[str]: List of public API names.
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

    # Match __all__ assignment with brackets or parentheses
    all_match = re.search(
        r'__all__\s*=\s*[\[\(](.*?)[\]\)]',
        content,
        re.DOTALL,
    )

    if not all_match:
        print("__all__ definition not found!")
        return []

    all_block = all_match.group(1)

    # Extract all quoted strings, skipping those on lines with `# doc:exclude`
    lines = all_block.splitlines()
    result = []

    for line in lines:
        if '# doc:exclude' in line:
            continue
        # Look for single or double quoted strings
        matches = re.findall(r'["\'](.*?)["\']', line)
        result.extend(matches)

    return result

def main(args):
    src_base_url = "https://github.com/wandb/wandb/tree/main/"
    valid_object_types = [ "module", "class", "function"]

    # Check if temporary directory exists. We use this directory to store generated markdown files.
    # A second script will process these files to clean them up.
    check_temp_dir(args.temp_output_directory)

    # Create MarkdownGenerator object. We use the same generator object for all APIs.
    generator = MarkdownGenerator(src_base_url=src_base_url)

    # To do: Remove this method of extracting public APIs from the __init__.py file.
    import_export_api_list = get_public_apis_from_init("/Users/noahluna/Documents/GitHub/wandb/wandb/apis/public/__init__.py")

    namespaces = {
        "public": {
            "file_path": "/Users/noahluna/Documents/GitHub/wandb/wandb/apis/public/__init__.py",
            "module": "wandb.apis.public",
            "apis_found": import_export_api_list
        } ,       
        "sdk": {
            "file_path": "/Users/noahluna/Documents/GitHub/wandb/wandb/__init__.template.pyi",
            "module": "wandb"
        },
        "launch": {
            "file_path": "/Users/noahluna/Documents/GitHub/wandb/wandb/sdk/launch/__init__.py",
            "module": "wandb.sdk.launch"
        },
    }

    # Get list of APIs from the __init__ files for each namespace
    for k in list(namespaces.keys()):
        print(k)
        if "apis_found" not in namespaces[k]:
            namespaces[k]["apis_found"] = get_api_list_from_init(namespaces[k]["file_path"])        

        for api in namespaces[k]["apis_found"]:
            
            print(k, api)
            module_obj = importlib.import_module(namespaces[k]["module"])
            docodile = DocodileMaker(module_obj, api, args.temp_output_directory)

            # Check if object type defined in source code is valid
            if docodile.object_type in valid_object_types:
                # Create markdown file for the API
                create_markdown(docodile, generator)

    # Generate overview markdown page
    # with open(os.path.join(os.getcwd(), args.temp_output_directory, "README.md"), 'w') as file:
    #     file.write(generator.overview2md())

if __name__  == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--temp_output_directory", default="wandb_sdk_docs", help="directory where the markdown files to process exist")
    args = parser.parse_args()
    main(args)
