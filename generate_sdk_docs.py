#!/bin/usr/python

import os
import re
import inspect
import argparse
import importlib
from inspect import isclass, isfunction, ismodule

from lazydocs import MarkdownGenerator
from typing import List, Type

from configuration import SOURCE 
import pydantic
from pydantic import BaseModel
from pydantic_settings import BaseSettings

###### USE LOCAL VERSION OF WANDB for debugging ######
import sys
from pathlib import Path

# Path to the local version of the `wandb` package
BASE_DIR = Path(__name__).resolve().parents[1] 
local_wandb_path = BASE_DIR / "wandb"
local_wandb_workspaces_path = BASE_DIR / "wandb-workspaces"

# Add the local package paths to sys.path
sys.path.insert(0, str(local_wandb_path))
sys.path.insert(0, str(local_wandb_workspaces_path))

# Confirm the correct version of wandb is being used
import wandb
print("Using wandb from:", wandb.__file__)
print("Wandb version:", wandb.__version__)

# Try to import wandb_workspaces if available
try:
    import wandb_workspaces
    print("Using wandb_workspaces from:", wandb_workspaces.__file__)
except ImportError:
    print("wandb_workspaces not found - Reports and Workspaces docs will not be generated")
###### END ######


# Temporary flag to hide launch APIs
# This is used to hide the launch APIs from the public API documentation.
HIDE_LAUNCH_APIS = True

class DocodileMaker:
    def __init__(self, module, api, output_dir, SOURCE):
        self.module = module
        self.api_item = api
        self.output_dir = output_dir
        self.ispydantic = False  # Flag to indicate if the object is a pydantic model
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

    def _check_pydantic(self):
        """Check if the object is a Pydantic model."""
        self.ispydantic = issubclass(self._object_attribute, BaseModel)

    @property
    def isPydantic(self):
        """Check if the object is a Pydantic model."""
        self._check_pydantic()
        return self.ispydantic

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

    if docodile.object_type == "function":
        return f"title: {base_name}()\n"
    elif docodile.object_type == "class":
        return f"title: {base_name}\n"
    else:
        return f"title: {base_name}\n"

def _type_key_string(docodile):
    """Checks the filepath and checks for substrings (e.g. "sdk", "data_type").
    
    Based on substring, determine the type of the object. Return the
    appropriate frontmatter string with the determined type.
    """
    # Check for specific class names for top-level SDK items
    file_path = docodile.getfile_path
    api_item = docodile.api_item if hasattr(docodile, 'api_item') else ""
    object_type = docodile.object_type if hasattr(docodile, 'object_type') else ""
    
    # Check for specific Artifact, Run, Settings classes - must be classes, not functions
    if "artifact" in file_path.lower() and ("Artifact" in api_item or "artifact.py" in file_path) and object_type == "class":
        return SOURCE["ARTIFACT"]["hugo_specs"]["frontmatter"] + "\n"
    elif api_item == "Run" and object_type == "class":
        # Only the Run class itself should go to RUN, not functions from wandb_run.py
        return SOURCE["RUN"]["hugo_specs"]["frontmatter"] + "\n"
    elif "wandb_settings" in file_path and api_item == "Settings" and object_type == "class":
        return SOURCE["SETTINGS"]["hugo_specs"]["frontmatter"] + "\n"
    # Check for Reports and Workspaces
    elif "wandb_workspaces" in file_path and "reports" in file_path:
        return SOURCE["REPORTS"]["hugo_specs"]["frontmatter"] + "\n"
    elif "wandb_workspaces" in file_path and "workspaces" in file_path:
        return SOURCE["WORKSPACES"]["hugo_specs"]["frontmatter"] + "\n"
    # Existing checks
    elif "sdk" and "data_type" in file_path: # Careful with data-type and data_type
        return SOURCE["DATATYPE"]["hugo_specs"]["frontmatter"] + "\n"
    elif "apis" and "public" in file_path:
        return SOURCE["PUBLIC_API"]["hugo_specs"]["frontmatter"] + "\n"
    elif "launch" in file_path and "LAUNCH_API" in SOURCE:
        return SOURCE.get("LAUNCH_API", SOURCE["SDK"])["hugo_specs"]["frontmatter"] + "\n"
    elif "automations" in file_path:
        return SOURCE["AUTOMATIONS"]["hugo_specs"]["frontmatter"] + "\n"
    elif "plot" in file_path:
        return SOURCE["CUSTOMCHARTS"]["hugo_specs"]["frontmatter"] + "\n"
    else:
        return SOURCE["SDK"]["hugo_specs"]["frontmatter"] + "\n"
 

def add_frontmatter(docodile):
    """Add frontmatter to the markdown file.
    
    Args:
        filename (str): Name of the file.
    """
    return "---\n" + _title_key_string(docodile) + _type_key_string(docodile) + _data_type_key_string(docodile) + "---\n\n"

def _data_type_key_string(docodile):
    """Add "function" or "Class" to the frontmatter."""
    return f"data_type_classification: {docodile.object_type}\n"

def _github_button(href_links):
    """To do: Add hugo scripting to add this function. For now, just add code line # for debugging.
    
    Args:
        href_links (str): URL for the GitHub button.
    """
    return "{{< cta-button githubLink=" + href_links + " >}}"+ "\n\n"


def format_github_button(filename, base_url="https://github.com/wandb/wandb/blob/main/"):
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

## TO DO: Make namepsace agnostic.
PROJECT_NAMESPACE = "wandb.automations"

def is_user_defined(method) -> bool:
    """
    Check if a method is defined in the project's namespace, explicitly excluding Pydantic.
    """
    module_name = getattr(method, "__module__", "")
    # Debug logging
    print(f"Checking method: {method.__name__}, module: {module_name}")
    
    # Explicitly exclude external libraries
    external_prefixes = ("pydantic", "pydantic_settings", "builtins", "typing")

    if any(module_name.startswith(prefix) for prefix in external_prefixes):
        print(f"Excluding {method.__name__} due to external prefix")
        return False
    
    result = module_name.startswith(PROJECT_NAMESPACE)
    print(f"Method {method.__name__} is_user_defined: {result}")
    return result

def generate_Pydantic_docstring(cls: Type[BaseSettings]) -> str:
    """
    Generate a Google-style class docstring with fields and user-defined methods only.

    Args:
        cls (Type[BaseSettings]): The Pydantic Settings class to document.

    Returns:
        str: A neatly formatted Google-style docstring.
    """
    # Get the class docstring
    class_docstring = inspect.getdoc(cls) or "No description provided."
    lines = [class_docstring, "", "Attributes:"]

    # Determine fields to document (repr=True)
    kept_field_names = {
        name for name, field_info in cls.model_fields.items() if field_info.repr
    }

    # Accumulate field descriptions from parent classes if missing
    field_docs = {}
    for base_cls in cls.__mro__:
        if not issubclass(base_cls, pydantic.BaseModel):
            continue
        for name, field_info in base_cls.model_fields.items():
            if name in kept_field_names and name not in field_docs:
                if field_info.description:
                    field_docs[name] = field_info.description

    # Get field descriptions and types, sorted alphabetically
    for field_name in sorted(kept_field_names):
        field_info = cls.model_fields[field_name]
        field_type = getattr(field_info.annotation, "__name__", str(field_info.annotation))
        description = inspect.cleandoc(field_docs.get(field_name, "No description provided."))
        print(f"Processing field: {field_name}, type: {field_type}, description: {description}")
        print("Description for field:", description)
        desc_lines = [line.strip() for line in description.splitlines() if line.strip()]

        lines.append(f"- {field_name} ({field_type}): {desc_lines[0]}")
        for extra_line in desc_lines[1:]:
            lines.append(f"    {extra_line}")

    # Document explicitly user-defined methods
    methods_seen = set()
    method_lines = [""]

    print(f"\nProcessing methods for class: {cls.__name__}")
    for base_cls in cls.__mro__:
        if base_cls is object:
            continue
        print(f"\nChecking base class: {base_cls.__name__}")
        # Get methods directly from class __dict__
        for name, member in base_cls.__dict__.items():
            print(f"\nExamining member: {name}")
            print(f"Member type: {type(member)}")
            # Skip private methods and already seen methods
            if name.startswith("_") or name in methods_seen:
                print(f"Skipping {name} - private or already seen")
                continue
            # Handle classmethod and staticmethod
            func = None
            if inspect.isfunction(member):
                print(f"{name} is a function")
                func = member
            elif isinstance(member, classmethod):
                print(f"{name} is a classmethod")
                func = member.__func__
            elif isinstance(member, staticmethod):
                print(f"{name} is a staticmethod")
                func = member.__func__
            if func is None:
                print(f"No function found for {name}")
                continue
            print(f"Function module: {getattr(func, '__module__', '')}")
            if is_user_defined(func):
                print(f"Adding {name} to documentation")
                methods_seen.add(name)
                signature = inspect.signature(func)
                docstring = inspect.getdoc(func) or "No description provided."
                cleaned_docstring = inspect.cleandoc(docstring).splitlines()

                method_lines.append(f"### <kbd>method</kbd> `{name}`")
                method_lines.append(f"```python\n{name}{signature}\n```")
                method_lines.append(f"{cleaned_docstring[0]}")
                for extra_line in cleaned_docstring[1:]:
                    method_lines.append(f"    {extra_line}")
            else:
                print(f"Skipping {name} - not user defined")

    if len(method_lines) > 2:
        lines.extend(method_lines)

    return "\n".join(lines)




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

        if docodile.object_type == "class" and docodile.isPydantic:
            print("Creating Pydantic class markdown", "\n\n")
            print(f"Generating docstring for Pydantic class: {docodile.api_item}")
            file.write(generate_Pydantic_docstring(docodile.object_attribute_value))
        elif docodile.object_type == "class" and not docodile.isPydantic:
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

    if HIDE_LAUNCH_APIS:
        modules.remove("jobs")
        modules.remove("query_generator")

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
    import_export_api_list = get_public_apis_from_init(local_wandb_path / "wandb" / "apis" / "public" / "__init__.py")
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
