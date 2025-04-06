#!/usr/bin/env python

import os
import shutil
import glob
import re
import yaml
import argparse

from configuration import SOURCE

def main(args):
    source_directory = args.source_directory
    root_directory = args.destination_directory

    # Ensure all destination subdirectories exist
    object_type_to_dir = {
        key: os.path.join(root_directory, subfolder["hugo_specs"]["folder_name"]) for key, subfolder in SOURCE.items()
    }
    
    for directory in object_type_to_dir.values():
        os.makedirs(directory, exist_ok=True)

    # Pattern to match YAML frontmatter
    frontmatter_pattern = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

    # Iterate over markdown files in the source directory
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
        target_dir = object_type_to_dir.get(object_type)

        if not target_dir:
            print(f"Skipping {filepath}: Unknown object_type '{object_type}'.")
            continue

        target_path = os.path.join(target_dir, os.path.basename(filepath))
        shutil.move(filepath, target_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory", default="wandb_sdk_docs", help="Directory where markdown files exist")
    parser.add_argument("--destination_directory", default="python-library", help="Root directory for processed files")
    args = parser.parse_args()
    main(args)
