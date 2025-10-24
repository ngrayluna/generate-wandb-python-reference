#!/bin/bash

TEMP_DIR=wandb_sdk_docs
DESTINATION_DIR=python

# Check if the directory exists, if it does, remove it else create it
if [ -d "$TEMP_DIR" ]; then
  echo "Directory '$TEMP_DIR' already exists. Removing it."
  rm -rf "$TEMP_DIR"
else
  echo "Directory '$TEMP_DIR' does not exist. Creating it."
fi

# Check if the destination directory exists, if it does, remove it else create it
if [ -d "$DESTINATION_DIR" ]; then
  echo "Directory '$DESTINATION_DIR' already exists. Removing it."
  rm -rf "$DESTINATION_DIR"
else
  echo "Directory '$DESTINATION_DIR' does not exist. Creating it."
fi

# Generate SDK docs using lazydocs
python generate_sdk_docs.py --temp_output_directory=$TEMP_DIR

# Process output doc created by lazydocs so it works with Docusaurus
python process_sdk_markdown.py --output_directory=$TEMP_DIR

# Make destination directory
mkdir -p $DESTINATION_DIR

# Sort and create subdirectories based on API or DataType
python sort_markdown_files.py --source_directory=$TEMP_DIR --destination_directory=$DESTINATION_DIR

python cleanup_directory.py --directory=$DESTINATION_DIR

# Create _index.md files
#python create_landing_pages.py --source_directory=$DESTINATION_DIR