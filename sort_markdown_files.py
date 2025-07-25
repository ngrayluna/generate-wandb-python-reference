#!/usr/bin/env python

import os
import shutil
import glob
import re
import yaml
import argparse
import ast
from pathlib import Path

from configuration import SOURCE

def build_local_paths(root_directory):
    """Create folders based on SOURCE and add local_path."""
    SOURCE_COPY = SOURCE.copy()
    
    # First create the sdk directory
    sdk_dir = os.path.join(root_directory, "sdk")
    os.makedirs(sdk_dir, exist_ok=True)
    
    for key, config in SOURCE_COPY.items():
        folder_name = config["hugo_specs"]["folder_name"]
        
        if key == "SDK":
            # Place SDK files directly in the sdk directory, not in a subdirectory
            local_path = sdk_dir
        elif key in ["DATATYPE", "CUSTOMCHARTS", "LAUNCH_API"]:
            # Place module in SDK Directory
            local_path = os.path.join(sdk_dir, folder_name)
        else:
            # Place other entries directly under root_directory
            local_path = os.path.join(root_directory, folder_name)
            
        SOURCE_COPY[key]["hugo_specs"]["local_path"] = local_path
        print(f"Creating directory: {local_path}")
        os.makedirs(local_path, exist_ok=True)

    return SOURCE_COPY


def create_object_type_lookup(source_dict):
    """Map object_type values from frontmatter to SOURCE keys.
    
    Creates a reverse index from SOURCE dict mapping—where the "object_type"
    value in the "frontmatter" is the key. E.g.

    "LAUNCH_API": {
    "module": "wandb.sdk.launch",
    "file_path": "/GitHub/wandb/wandb/sdk/launch/__init__.py",
    "hugo_specs": {
        "title": "Launch Library",
        "description": "A collection of launch APIs for W&B.",
        "frontmatter": "object_type: launch_apis_namespace",
        "folder_name": "launch-library",
    },

    This is a utility function that creates a dictionary mapping
    object_type values found in the frontmatter to their corresponding
    keys in the SOURCE dictionary. This allows for easy lookup when
    sorting markdown files based on their object_type.

    Args:
        source_dict (dict): The SOURCE dictionary containing the configuration.
    """
    return {
        v["hugo_specs"]["frontmatter"].split(": ")[1]: k for k, v in source_dict.items()
    }

def sort_markdown_files(source_directory, source_copy):
    """Read markdown files, extract object_type, and sort them."""

    # Create dictionary where the keys are object_type values from frontmatter
    # and the values are the corresponding keys in the SOURCE dictionary
    # Returns something lke:
    # {'api': 'SDK', 'data-type': 'DATATYPE', 'public_apis_namespace': 'PUBLIC_API', 'launch_apis_namespace': 'LAUNCH_API'}
    object_type_to_key = create_object_type_lookup(source_copy)

    # Create a set to keep track of directories created
    directories_created = []

    for filepath in glob.glob(os.path.join(os.getcwd(), source_directory, '*.md')):

        # Get the frontmatter from the markdown file
        frontmatter = read_markdown_metadata(filepath)

        object_type = frontmatter.get("object_type")
        if not object_type:
            print(f"Skipping {filepath}: No object_type in frontmatter.")
            continue

        source_key = object_type_to_key.get(object_type)
        if not source_key:
            print(f"Skipping {filepath}: Unknown object_type '{object_type}'.")
            continue

        # Get the destination directory from the SOURCE dictionary
        destination_dir = source_copy[source_key]["hugo_specs"]["local_path"]
        
        # Keep track of directories created this is used to do further processing later
        directories_created.append(destination_dir)  

        destination_path = os.path.join(destination_dir, os.path.basename(filepath))

        print(f"Copying to {destination_path}")
        shutil.copy(filepath, destination_path)

    return set(directories_created)


def read_markdown_metadata(filepath):
    """Read the frontmatter metadata from a markdown file."""
    with open(filepath, 'r') as file:
        content = file.read()

    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        print(f"Error parsing frontmatter in {filepath}: {e}")
        return None

    return frontmatter

def sort_functions_and_classes(filepath):
    """Sort functions and classes into their own directories."""
    # Create a new directory for functions and classes
    functions_dir = os.path.join(os.getcwd(), filepath, "functions")
    classes_dir = os.path.join(os.getcwd(), filepath, "classes")
    os.makedirs(functions_dir, exist_ok=True)
    os.makedirs(classes_dir, exist_ok=True)

    # Move the functions and classes into their respective directories
    for filepath in glob.glob(os.path.join(os.getcwd(), filepath, '*.md')):
        frontmatter = read_markdown_metadata(filepath)
        datatype = frontmatter.get("data_type_classification")
        if not datatype:
            print(f"Skipping {filepath}: No data_type_classification in frontmatter.")

        if "function" in datatype:
            shutil.move(filepath, functions_dir)
        elif "class" in datatype:
            shutil.move(filepath, classes_dir)

    return


def main(args):
    source_directory = args.source_directory
    root_directory = args.destination_directory

    # Define the global module path. This has a list of legacy functions that we need to extract but don't advise using.
    BASE_DIR = Path(__name__).resolve().parents[1] 
    global_module_path = BASE_DIR / "wandb" / "wandb" / "sdk" / "lib" / "module.py"

    # Step 1: Build folder structure and local_path mapping
    source_copy = build_local_paths(root_directory)

    # Step 2: Sort markdown files based on frontmatter
    # Returns a set of directories created
    # Returns: {'python/sdk/data-type', 'python/automations', 'python/sdk/actions', ...}
    directories_created = sort_markdown_files(source_directory, source_copy)

    # Grab whatever the directory "action" APIs are in
    # Since SDK files are now placed directly in the sdk directory, look for that
    sdk_path = source_copy["SDK"]["hugo_specs"]["local_path"]
    
    # Find the sdk directory in the created directories
    global_fun_root_path = None
    for partial_path in directories_created:
        if partial_path == sdk_path:
            global_fun_root_path = partial_path
            break
    print(f"Found global_dir_root: {global_fun_root_path}")

    # Step 3: Sort functions and classes into their own directories
    sort_functions_and_classes(global_fun_root_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory", default="wandb_sdk_docs", help="Directory where markdown files exist")
    parser.add_argument("--destination_directory", default="python", help="Root directory for processed files")
    args = parser.parse_args()
    main(args)
