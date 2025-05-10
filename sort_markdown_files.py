#!/usr/bin/env python

import os
import shutil
import glob
import re
import yaml
import argparse

from configuration import SOURCE

def build_local_paths(root_directory):
    """Create folders based on SOURCE and add local_path."""
    SOURCE_COPY = SOURCE.copy()
    
    # First create the sdk directory
    sdk_dir = os.path.join(root_directory, "sdk")
    os.makedirs(sdk_dir, exist_ok=True)
    
    for key, config in SOURCE_COPY.items():
        folder_name = config["hugo_specs"]["folder_name"]
        
        if key in ["SDK", "DATATYPE", "LAUNCH_API"]:
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
    frontmatter_pattern = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

    # Create dictionary where the keys are object_type values from frontmatter
    # and the values are the corresponding keys in the SOURCE dictionary
    object_type_to_key = create_object_type_lookup(source_copy)
    # Returns something lke:
    # {'api': 'SDK', 'data-type': 'DATATYPE', 'public_apis_namespace': 'PUBLIC_API', 'launch_apis_namespace': 'LAUNCH_API'}

    for filepath in glob.glob(os.path.join(os.getcwd(), source_directory, '*.md')):
        print(f"Reading in {filepath} for sorting...")

        with open(filepath, 'r') as file:
            content = file.read()

        match = frontmatter_pattern.match(content)
        if not match:
            print(f"Skipping {filepath}: No frontmatter found.")
            continue

        try:
            frontmatter = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            print(f"Error parsing frontmatter in {filepath}: {e}")
            continue

        object_type = frontmatter.get("object_type")
        if not object_type:
            print(f"Skipping {filepath}: No object_type in frontmatter.")
            continue

        source_key = object_type_to_key.get(object_type)
        if not source_key:
            print(f"Skipping {filepath}: Unknown object_type '{object_type}'.")
            continue

        destination_dir = source_copy[source_key]["hugo_specs"]["local_path"]
        destination_path = os.path.join(destination_dir, os.path.basename(filepath))
        print(f"Copying to {destination_path}")
        shutil.copy(filepath, destination_path)

def main(args):
    source_directory = args.source_directory
    root_directory = args.destination_directory

    # Step 1: Build folder structure and local_path mapping
    source_copy = build_local_paths(root_directory)

    # Step 2: Sort markdown files based on frontmatter
    sort_markdown_files(source_directory, source_copy)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory", default="wandb_sdk_docs", help="Directory where markdown files exist")
    parser.add_argument("--destination_directory", default="python-library", help="Root directory for processed files")
    args = parser.parse_args()
    main(args)
