#!/bin/usr/python

import os
import re
import inspect
import argparse
import importlib  # make sure this is at the top
from inspect import isclass, isfunction, ismodule

from lazydocs import MarkdownGenerator
from typing import List, Type, Union, Dict, Tuple, Any, Literal, get_args, get_origin

from configuration import SOURCE 
import pydantic
from pydantic import BaseModel
from pydantic_settings import BaseSettings


###############################################################################
# USE LOCAL VERSION OF WANDB for debugging
import sys
from pathlib import Path

# Path to the local version of the `wandb` package
BASE_DIR = Path(__name__).resolve().parents[1] 
local_wandb_path = BASE_DIR / "wandb"

# Add the local package path to sys.path
sys.path.insert(0, str(local_wandb_path))

# Confirm the correct version of wandb is being used
import wandb
print("Using wandb from:", wandb.__file__)
print("Wandb version:", wandb.__version__)
###############################################################################


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
    if "sdk" and "data_type" in docodile.getfile_path: # Careful with data-type and data_type
        return SOURCE["DATATYPE"]["hugo_specs"]["frontmatter"] + "\n"
    elif "apis" and "public" in docodile.getfile_path:
        return SOURCE["PUBLIC_API"]["hugo_specs"]["frontmatter"] + "\n"
    elif "launch" in docodile.getfile_path:
        return SOURCE["LAUNCH_API"]["hugo_specs"]["frontmatter"] + "\n"
    elif "automations" in docodile.getfile_path:
        return SOURCE["AUTOMATIONS"]["hugo_specs"]["frontmatter"] + "\n"
    elif "plot" in docodile.getfile_path:
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
    return f"python_object_type: {docodile.object_type}\n"

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

def custom_class2md(cls: Any, generator) -> str:
    """Custom class documentation generator that includes property return types.
    
    This function extends lazydocs' class2md to properly document property return types.
    
    Args:
        cls: The class to document
        generator: The MarkdownGenerator instance from lazydocs
        
    Returns:
        Markdown documentation for the class with property return types
    """
    # Start with the default lazydocs output
    base_output = generator.class2md(cls)
    
    # Find and enhance property documentation
    lines = base_output.split('\n')
    enhanced_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a property line
        if '<kbd>property</kbd>' in line:
            # Extract property name from the line
            import re
            match = re.search(r'<kbd>property</kbd>\s+(\w+\.)?(\w+)', line)
            if match:
                prop_name = match.group(2)
                
                # Try to get the property from the class
                try:
                    prop_obj = getattr(cls, prop_name)
                    if isinstance(prop_obj, property) and prop_obj.fget:
                        # Get the return type annotation
                        sig = inspect.signature(prop_obj.fget)
                        if sig.return_annotation != inspect.Parameter.empty:
                            # Format the return type
                            return_type = _format_type_for_display(sig.return_annotation)
                            
                            # Add the line with property name
                            enhanced_lines.append(line)
                            
                            # Collect all docstring lines until we hit the separator
                            i += 1
                            docstring_lines = []
                            while i < len(lines) and not lines[i].startswith('---'):
                                docstring_lines.append(lines[i])
                                i += 1
                                
                            # Add the docstring
                            for doc_line in docstring_lines:
                                enhanced_lines.append(doc_line)
                                
                            # Add return type information if there was a docstring
                            if any(line.strip() for line in docstring_lines):
                                enhanced_lines.append("")
                                enhanced_lines.append("")
                                enhanced_lines.append("**Returns:**")
                                enhanced_lines.append(f" - `{return_type}`: The {prop_name} property value.")
                            
                            # We've already processed up to the separator, so continue from here
                            i -= 1  # Back up one since we'll increment at the bottom of the loop
                            
                            # Skip to next iteration
                            i += 1
                            continue
                except (AttributeError, TypeError):
                    pass
        
        enhanced_lines.append(line)
        i += 1
    
    return '\n'.join(enhanced_lines)


def _format_type_for_display(annotation) -> str:
    """Format a type annotation for display in documentation.
    
    Args:
        annotation: Type annotation to format
        
    Returns:
        Formatted string representation of the type
    """
    if annotation is None:
        return "Any"
    
    # Handle string annotations
    if isinstance(annotation, str):
        return annotation
        
    # Handle None type
    if annotation is type(None):
        return "None"
        
    # Get the origin and args for generic types
    origin = get_origin(annotation)
    args = get_args(annotation)
    
    # Handle Union types (including Optional)
    if origin is Union:
        formatted_args = [_format_type_for_display(arg) for arg in args]
        return " | ".join(formatted_args)
    
    # Handle List types
    if origin in (list, List):
        if args:
            inner_type = _format_type_for_display(args[0])
            return f"list[{inner_type}]"
        return "list"
    
    # Handle Dict types
    if origin in (dict, Dict):
        if args and len(args) == 2:
            key_type = _format_type_for_display(args[0])
            value_type = _format_type_for_display(args[1])
            return f"dict[{key_type}, {value_type}]"
        return "dict"
        
    # Handle Tuple types
    if origin in (tuple, Tuple):
        if args:
            formatted_args = [_format_type_for_display(arg) for arg in args]
            return f"tuple[{', '.join(formatted_args)}]"
        return "tuple"
    
    # Handle basic types
    if hasattr(annotation, '__name__'):
        return annotation.__name__
    
    # Fallback to string representation
    return str(annotation).replace('typing.', '')


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
            # Use the new Google-style docstring generator
            file.write(generate_google_style_pydantic_docstring(docodile.object_attribute_value))
        elif docodile.object_type == "class" and not docodile.isPydantic:
            print("Creating class markdown", "\n\n")
            # Use custom class2md that handles properties with return types
            file.write(custom_class2md(docodile.object_attribute_value, generator))        
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



def generate_google_style_pydantic_docstring(cls: Type[BaseModel]) -> str:
    """Generate a Google-style docstring for a Pydantic model.
    
    This function creates comprehensive documentation for Pydantic models
    following the specified format with <kbd> tags and proper formatting.
    
    Args:
        cls: A Pydantic BaseModel class to document.
        
    Returns:
        A formatted Google-style docstring as a string.
    """
    
    # Start with class header and docstring
    class_doc = inspect.getdoc(cls) or ""
    lines = [f"## <kbd>class</kbd> `{cls.__name__}`"]
    if class_doc:
        lines.append(class_doc)
    lines.append("")
    lines.append("")

    # Add __init__ method documentation with signature
    lines.append(f"### <kbd>method</kbd> `{cls.__name__}.__init__`")
    lines.append("")
    lines.append("```python")
    
    # Build __init__ signature from model fields
    init_params = []
    for field_name, field_info in cls.model_fields.items():
        # Format type annotation with quotes
        field_type = _format_type_with_quotes(field_info.annotation)
        
        # Check if field has a default value
        from pydantic_core import PydanticUndefined
        
        if field_info.default is not PydanticUndefined:
            # Field has an explicit default
            default_val = repr(field_info.default)
            init_params.append(f"    {field_name}: '{field_type}' = {default_val}")
        elif field_info.default_factory is not None:
            # Field has a default factory - show as None for simplicity
            init_params.append(f"    {field_name}: '{field_type}' = None")
        else:
            # Required field with no default
            init_params.append(f"    {field_name}: '{field_type}'")
    
    if init_params:
        lines.append("__init__(")
        lines.append(",\n".join(init_params))
        lines.append(") → None")
    else:
        lines.append("__init__(self) → None")
    
    lines.append("```")
    lines.append("")

    # Add Args section for fields
    if cls.model_fields:
        lines.append("**Args:**")
        lines.append(" ")
        
        # Process each field
        for field_name, field_info in cls.model_fields.items():
            # Get field type without quotes for args section
            field_type = _format_pydantic_type(field_info.annotation)
            
            # Get field description from Pydantic field info
            description = field_info.description or ""
            
            # Handle multi-line descriptions
            if description:
                # Split description into lines
                desc_lines = description.split('\n')
                # Remove empty lines at the beginning and end
                while desc_lines and not desc_lines[0].strip():
                    desc_lines.pop(0)
                while desc_lines and not desc_lines[-1].strip():
                    desc_lines.pop()
                
                if desc_lines:
                    # First line of description
                    lines.append(f" - `{field_name}` ({field_type}): {desc_lines[0].strip()}")
                    
                    # Add remaining lines with proper indentation
                    for desc_line in desc_lines[1:]:
                        stripped = desc_line.strip()
                        if stripped:  # Only add non-empty lines
                            lines.append(f"   {stripped}")
                else:
                    # Empty description
                    lines.append(f" - `{field_name}` ({field_type}): ")
            else:
                # No description
                lines.append(f" - `{field_name}` ({field_type}): ")
        
        lines.append("")
    
    # Add Returns section
    lines.append("**Returns:**")
    lines.append(f" An `{cls.__name__}` object.")
    lines.append("")
    
    # Add user-defined methods, properties, and classmethods
    methods = _get_pydantic_user_methods_properties_classmethods(cls)
    for method_name, method_obj, method_type in methods:
        # Determine the appropriate tag
        if method_type == "property":
            lines.append(f"### <kbd>property</kbd> `{cls.__name__}.{method_name}`")
        elif method_type == "classmethod":
            lines.append(f"### <kbd>classmethod</kbd> `{cls.__name__}.{method_name}`")
        else:  # regular method
            lines.append(f"### <kbd>method</kbd> `{cls.__name__}.{method_name}`")
        
        lines.append("")
        
        # Add code block with signature for methods (not properties)
        if method_type != "property":
            lines.append("```python")
            
            # Get method signature
            sig = inspect.signature(method_obj)
            
            # Format parameters
            params = []
            for param_name, param in sig.parameters.items():
                # Skip 'self' for instance methods, 'cls' for classmethods
                if param_name in ('self', 'cls'):
                    continue
                    
                if param.annotation != inspect.Parameter.empty:
                    param_type = _format_type_with_quotes(param.annotation)
                    if param.default != inspect.Parameter.empty:
                        default_val = repr(param.default)
                        params.append(f"    {param_name}: '{param_type}' = {default_val}")
                    else:
                        params.append(f"    {param_name}: '{param_type}'")
                else:
                    if param.default != inspect.Parameter.empty:
                        params.append(f"    {param_name} = {repr(param.default)}")
                    else:
                        params.append(f"    {param_name}")
            
            # Format return type
            return_type = "None"
            if sig.return_annotation != inspect.Parameter.empty:
                return_type = _format_type_with_quotes(sig.return_annotation)
            
            if params:
                lines.append(f"{method_name}(")
                lines.append(",\n".join(params))
                lines.append(f") → {return_type}")
            else:
                lines.append(f"{method_name}() → {return_type}")
            
            lines.append("```")
            lines.append("")
        
        # Parse and add method documentation
        method_doc = inspect.getdoc(method_obj)
        if method_doc:
            if method_type == "property":
                # For properties, add the docstring and return type
                lines.append(method_doc)
                
                # Try to get the return type annotation if available
                if method_obj:  # method_obj is the fget function for properties
                    try:
                        sig = inspect.signature(method_obj)
                        if sig.return_annotation != inspect.Parameter.empty:
                            return_type = _format_type_for_display(sig.return_annotation)
                            lines.append("")
                            lines.append("**Returns:**")
                            lines.append(f" - `{return_type}`: The {method_name} property value.")
                    except (TypeError, ValueError):
                        pass  # If we can't get signature, just skip return type
                
                lines.append("")
            else:
                parsed_doc = _parse_google_docstring(method_doc)
                
                # Add description
                if parsed_doc['description']:
                    lines.append(parsed_doc['description'])
                    lines.append("")
                
                # Add Args section if present
                if parsed_doc['args']:
                    lines.append("**Args:**")
                    lines.append(" ")
                    for arg_name, arg_desc in parsed_doc['args'].items():
                        lines.append(f" - `{arg_name}`: {arg_desc}")
                    lines.append("")
                    
                # Add Returns section if present
                if parsed_doc['returns']:
                    lines.append("**Returns:**")
                    lines.append(f" - {parsed_doc['returns']}")
                    lines.append("")
                    
                # Add Raises section if present
                if parsed_doc['raises']:
                    lines.append("**Raises:**")
                    for exc_type, exc_desc in parsed_doc['raises'].items():
                        lines.append(f" - `{exc_type}`: {exc_desc}")
                    lines.append("")
    
    return "\n".join(lines)


def _format_type_with_quotes(annotation) -> str:
    """Format a type annotation with appropriate quotes for signature display.
    
    Converts types to their string representation suitable for quoted display.
    """
    if annotation is None:
        return "Any"
        
    # Handle None type
    if annotation is type(None):
        return "None"
        
    # Get the origin and args for generic types
    origin = get_origin(annotation)
    args = get_args(annotation)
    
    # Handle Optional types (Union with None)
    if origin is Union:
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            # This is Optional[T]
            inner_type = _format_type_with_quotes(non_none_args[0])
            return f"{inner_type} | None"
        else:
            # This is a Union of multiple types
            formatted_args = [_format_type_with_quotes(arg) for arg in args]
            return " | ".join(formatted_args)
    
    # Handle List types
    if origin in (list, List):
        if args:
            inner_type = _format_type_with_quotes(args[0])
            return f"list[{inner_type}]"
        return "list"
    
    # Handle Dict types
    if origin in (dict, Dict):
        if args and len(args) == 2:
            key_type = _format_type_with_quotes(args[0])
            value_type = _format_type_with_quotes(args[1])
            return f"dict[{key_type}, {value_type}]"
        return "dict"
        
    # Handle Tuple types
    if origin in (tuple, Tuple):
        if args:
            formatted_args = [_format_type_with_quotes(arg) for arg in args]
            return f"tuple[{', '.join(formatted_args)}]"
        return "tuple"
    
    # Handle Literal types
    if origin is Literal:
        values = ', '.join(repr(arg) for arg in args)
        return f"Literal[{values}]"
    
    # Handle basic types
    if hasattr(annotation, '__name__'):
        # Use lowercase for basic types in modern Python style
        if annotation.__name__ in ('str', 'int', 'float', 'bool', 'bytes'):
            return annotation.__name__
        return annotation.__name__
    
    # Fallback to string representation
    return str(annotation).replace('typing.', '')


def _format_pydantic_type(annotation) -> str:
    """Format a type annotation for display in documentation.
    
    Handles Optional, List, Dict, Union and other complex types.
    """
    
    if annotation is None:
        return "Any"
        
    # Handle None type
    if annotation is type(None):
        return "None"
        
    # Get the origin and args for generic types
    origin = get_origin(annotation)
    args = get_args(annotation)
    
    # Handle Optional types (Union with None)
    if origin is Union:
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            # This is Optional[T]
            inner_type = _format_pydantic_type(non_none_args[0])
            return f"Optional[{inner_type}]"
        else:
            # This is a Union of multiple types
            formatted_args = [_format_pydantic_type(arg) for arg in args]
            return f"Union[{', '.join(formatted_args)}]"
    
    # Handle List types
    if origin in (list, List):
        if args:
            inner_type = _format_pydantic_type(args[0])
            return f"List[{inner_type}]"
        return "List"
    
    # Handle Dict types
    if origin in (dict, Dict):
        if args and len(args) == 2:
            key_type = _format_pydantic_type(args[0])
            value_type = _format_pydantic_type(args[1])
            return f"Dict[{key_type}, {value_type}]"
        return "Dict"
        
    # Handle Tuple types
    if origin in (tuple, Tuple):
        if args:
            formatted_args = [_format_pydantic_type(arg) for arg in args]
            return f"Tuple[{', '.join(formatted_args)}]"
        return "Tuple"
    
    # Handle Literal types
    if origin is Literal:
        values = ', '.join(repr(arg) for arg in args)
        return f"Literal[{values}]"
    
    # Handle basic types and classes
    if hasattr(annotation, '__name__'):
        return annotation.__name__
    
    # Fallback to string representation
    return str(annotation).replace('typing.', '')


def _get_pydantic_user_methods_properties_classmethods(cls: Type[BaseModel]) -> List[Tuple[str, Any, str]]:
    """Get user-defined methods, properties, and classmethods from a Pydantic model.
    
    Filters out Pydantic internal methods and inherited BaseModel methods.
    Returns tuples of (name, object, type) where type is 'method', 'property', or 'classmethod'.
    """
    methods = []
    
    # Skip Pydantic internal methods
    pydantic_methods = {
        'model_config', 'model_fields', 'model_computed_fields',
        'model_validate', 'model_validate_json', 'model_dump',
        'model_dump_json', 'model_copy', 'model_construct',
        'model_json_schema', 'model_parametrized_name',
        'model_rebuild', 'model_post_init', 'dict', 'json',
        'parse_obj', 'parse_raw', 'parse_file', 'from_orm',
        'schema', 'schema_json', 'construct', 'copy',
        'update_forward_refs', '__get_validators__',
        'validate', '__fields__', '__config__'
    }
    
    # Iterate through the class's own __dict__ to find user-defined methods
    for name, obj in cls.__dict__.items():
        # Skip private/magic methods
        if name.startswith('_'):
            continue
            
        # Skip Pydantic internal methods
        if name in pydantic_methods:
            continue
        
        # Check if it's a property
        if isinstance(obj, property):
            methods.append((name, obj.fget, 'property'))
        # Check if it's a classmethod
        elif isinstance(obj, classmethod):
            methods.append((name, obj.__func__, 'classmethod'))
        # Check if it's a regular method
        elif inspect.isfunction(obj):
            methods.append((name, obj, 'method'))
                
    return methods




def _parse_google_docstring(docstring: str) -> dict:
    """Parse a Google-style docstring into sections.
    
    Returns a dictionary with keys: description, args, returns, raises
    """
    if not docstring:
        return {'description': '', 'args': {}, 'returns': '', 'raises': {}}
    
    lines = docstring.split('\n')
    result = {'description': '', 'args': {}, 'returns': '', 'raises': {}}
    
    current_section = 'description'
    current_arg = None
    current_exception = None
    description_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check for section headers
        if stripped in ('Args:', 'Arguments:', 'Parameters:'):
            current_section = 'args'
            current_arg = None
            i += 1
            continue
        elif stripped in ('Returns:', 'Return:'):
            current_section = 'returns'
            i += 1
            continue
        elif stripped in ('Raises:', 'Raise:'):
            current_section = 'raises'
            current_exception = None
            i += 1
            continue
            
        # Process content based on current section
        if current_section == 'description':
            description_lines.append(line)
            
        elif current_section == 'args':
            # Check if this is a new argument (not indented or indented at arg level)
            if stripped and not line.startswith('        '):
                # Parse "arg_name (type): description" or "arg_name: description"
                if ':' in line:
                    parts = line.strip().split(':', 1)
                    arg_part = parts[0].strip()
                    desc_part = parts[1].strip() if len(parts) > 1 else ''
                    
                    # Remove type annotation if present
                    if '(' in arg_part and ')' in arg_part:
                        arg_name = arg_part[:arg_part.index('(')].strip()
                    else:
                        arg_name = arg_part
                        
                    current_arg = arg_name
                    result['args'][current_arg] = desc_part
            elif current_arg and line.startswith('        '):
                # Continuation of current arg description
                result['args'][current_arg] += ' ' + line.strip()
                
        elif current_section == 'returns':
            if result['returns']:
                result['returns'] += ' ' + line.strip()
            else:
                result['returns'] = line.strip()
                
        elif current_section == 'raises':
            # Check if this is a new exception
            if stripped and not line.startswith('        '):
                if ':' in line:
                    parts = line.strip().split(':', 1)
                    exc_type = parts[0].strip()
                    exc_desc = parts[1].strip() if len(parts) > 1 else ''
                    current_exception = exc_type
                    result['raises'][current_exception] = exc_desc
            elif current_exception and line.startswith('        '):
                # Continuation of current exception description
                result['raises'][current_exception] += ' ' + line.strip()
                
        i += 1
    
    # Join description lines
    result['description'] = '\n'.join(description_lines).strip()
    
    return result


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

    # Get list of APIs from the __init__ files for each namespace
    # and add to the SOURCE_DICT_COPY dictionary.
    for k in list(SOURCE_DICT_COPY.keys()): # Returns key from configuration.py ['SDK', 'DATATYPE', 'LAUNCH_API', 'PUBLIC_API', 'AUTOMATIONS']

        # Get the list of APIs from the __init__.py or .pyi file
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
