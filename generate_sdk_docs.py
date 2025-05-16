#!/bin/usr/python

import os
import re
import inspect
import argparse
import importlib  # make sure this is at the top
from inspect import isclass, isfunction, ismodule

# import wandb
from lazydocs import MarkdownGenerator
from typing import List

from configuration import SOURCE 


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
    def __init__(self, module, api, output_dir, SOURCE):
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
        attr = self._object_attribute
        if isclass(attr):
            self._object_type = "class"
        elif isfunction(attr):
            self._object_type = "function"
        elif ismodule(attr):
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
    """Checks the filepath and checks for substrings (e.g. "sdk", "data_type").
    
    Based on substring, determine the type of the object. Return the
    appropriate frontmatter string with the determined type.
    """
    if "sdk" and "data_type" in docodile.getfile_path: # Careful with data-type and data_type
        return SOURCE["DATATYPE"]["hugo_specs"]["frontmatter"] + "\n"
    elif "apis" and "public" in docodile.getfile_path:
        return SOURCE["PUBLIC_API"]["hugo_specs"]["frontmatter"] + "\n"
    elif "launch" in docodile.getfile_path:
        return SOURCE["LAUNCH_API"]["hugo_specs"]["frontmatter"] + "\n"
    elif "automations" in docodile.getfile_path:
        return SOURCE["AUTOMATIONS"]["hugo_specs"]["frontmatter"] + "\n"
    else:
        return SOURCE["SDK"]["hugo_specs"]["frontmatter"] + "\n"

def get_type_key_string(self):
    # Make a method that returns the definition specified
    # in _type_key_string
    return    

def add_frontmatter(docodile):
    """Add frontmatter to the markdown file.
    
    Args:
        filename (str): Name of the file.
    """
    return "---\n" + _title_key_string(docodile) + _type_key_string(docodile) + _data_type_key_string(docodile) + "---\n\n"

def _data_type_key_string(docodile):
    return f"data_type_classification: {docodile.object_type}\n"


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

def get_symbol_module_map(pyi_path: str) -> dict[str, str]:
    """
    Build a basic map of symbol -> actual module from `from ... import ...` statements.
    """

    mapping = {}
    import_pattern = re.compile(r"from ([\w\.]+) import (.+)")

    with open(pyi_path, "r") as f:
        for line in f:
            match = import_pattern.match(line.strip())
            if match:
                module_path, symbols = match.groups()
                for part in symbols.split(","):
                    part = part.strip()
                    if " as " in part:
                        original, alias = [x.strip() for x in part.split(" as ")]
                        mapping[alias] = module_path
                    else:
                        mapping[part] = module_path
    return mapping



def main(args):
    src_base_url = "https://github.com/wandb/wandb/tree/main/"
    valid_object_types = [ "module", "class", "function"]

    # Check if temporary directory exists. We use this directory to store generated markdown files.
    # A second script will process these files to clean them up.
    check_temp_dir(args.temp_output_directory)

    # Create MarkdownGenerator object. We use the same generator object for all APIs.
    # Using the same generator enables us to create an overview markdown page if needed.
    generator = MarkdownGenerator(src_base_url=src_base_url)

    # Make a copy of the SOURCE dictionary to avoid modifying the original
    SOURCE_DICT_COPY = SOURCE.copy()  

    ## Temporary ##
    # To do: Remove this method of extracting public APIs from the __init__.py file.
    import_export_api_list = get_public_apis_from_init("/Users/noahluna/Documents/GitHub/wandb/wandb/apis/public/__init__.py")
    SOURCE_DICT_COPY["PUBLIC_API"]["apis_found"] = import_export_api_list
    ## End Temporary ##

    # Get list of APIs from the __init__ files for each namespace
    # and add to the SOURCE_DICT_COPY dictionary.
    for k in list(SOURCE_DICT_COPY.keys()): # Returns key from configuration.py ['SDK', 'DATATYPE', 'LAUNCH_API', 'PUBLIC_API', 'AUTOMATIONS']

        # Get APIs for each namespace
        if "apis_found" not in SOURCE_DICT_COPY[k]:
            # Go through each key in the SOURCE dictionary 
            # Returns top level keys in SOURCE dict and stores into list ['SDK', 'DATATYPE', 'LAUNCH_API', 'PUBLIC_API', 'AUTOMATIONS']
            SOURCE_DICT_COPY[k]["apis_found"] = get_api_list_from_init(SOURCE_DICT_COPY[k]["file_path"])

        # Get the symbol to module mapping for each API
        # Returns a dict of symbol to module mapping
        # e.g.  {'Api': 'wandb.apis.public.api', 'RetryingClient': 'wandb.apis.public.api', ...}
        symbol_to_module = get_symbol_module_map(SOURCE_DICT_COPY[k]["file_path"]) 
        
        # Get the list of APIs for the current namespace
        for api in SOURCE_DICT_COPY[k]["apis_found"]:
            # Get the fallback module from the SOURCE dictionary # e.g. "wandb.apis.public"
            fallback_module = SOURCE_DICT_COPY[k]["module"] 
            # Get the resolved module from the symbol_to_module mapping
            # This is used because the API may be imported from a different module
            # e.g. Run is declared in wandb.__init__.template.pyi as part of __all__,
            # while actually being defined in another submodule, wandb.sdk.wandb_run.
            resolved_module = symbol_to_module.get(api, fallback_module)

            try:
                # Always import the fallback module (top-level package)
                module_obj = importlib.import_module(fallback_module)

                # Try to retrieve the attribute
                if hasattr(module_obj, api):
                    docodile = DocodileMaker(module_obj, api, args.temp_output_directory, SOURCE)
                else:
                    # Try resolved module only if different
                    if resolved_module != fallback_module:
                        sub_module_obj = importlib.import_module(resolved_module)
                        docodile = DocodileMaker(sub_module_obj, api, args.temp_output_directory, SOURCE)
                    else:
                        print(f"[WARN] {api} not found in {fallback_module}")
                        continue

                if docodile.object_type in valid_object_types:
                    create_markdown(docodile, generator)
                else:
                    print(f"[WARN] Unsupported type for: {api}")

            except (ImportError, AttributeError, TypeError) as e:
                print(f"[ERROR] Failed to resolve {api} from {resolved_module}: {e}")


if __name__  == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--temp_output_directory", default="wandb_sdk_docs", help="directory where the markdown files to process exist")
    args = parser.parse_args()
    main(args)
