#!/bin/usr/python

import os 
import shutil
import glob
import re
import yaml
import argparse

def main(args):
    # Directory with processed files
    source_directory = args.source_directory
    root_directory = args.destination_directory

    # Ensure root and subdir exist
    api_dir = os.path.join(root_directory, "api")
    data_type_dir = os.path.join(root_directory, "data_type")
    os.makedirs(api_dir, exist_ok=True)
    os.makedirs(data_type_dir, exist_ok=True)

    # Pattern to match YAML frontmatter
    frontmatter_pattern = re.compile(r"^---\n(.*?)\n---", re.DOTALL)    

     # Iterate over markdown files in source directory
    for filepath in glob.glob(os.path.join(os.getcwd(), source_directory, '*.md')):
        print(f"Reading in {filepath} for processing...")

        # Read markdown content from file
        with open(filepath, 'r') as file:
            content = file.read()

            # Extract frontmatter using regex
            match = frontmatter_pattern.match(content)
            if not match:
                print(f"Skipping {filepath}: No frontmatter found.")
                continue

            # Parse the frontmatter YAML
            try:
                frontmatter = yaml.safe_load(match.group(1))
            except yaml.YAMLError as e:
                print(f"Error parsing frontmatter in {filepath}: {e}")
                continue

            # Determine the target directory based on 'object_type'
            object_type = frontmatter.get("object_type")
            if object_type == "api":
                target_dir = api_dir
            elif object_type == "data_type":
                target_dir = data_type_dir
            else:
                print(f"Skipping {filepath}: Unknown object_type '{object_type}'.")
                continue

            # Move the file to the target directory
            target_path = os.path.join(target_dir, os.path.basename(filepath))
            shutil.move(filepath, target_path)
            print(f"Moved {filepath} to {target_path}")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory", default="wandb_sdk_docs", help="directory where the markdown files to process exist")
    parser.add_argument("--destination_directory", default="python-library", help="root directory for the processed files")
    args = parser.parse_args()
    main(args)