#!/bin/bash

TEMP_DIR=wandb_sdk_docs
DESTINATION_DIR=python-library
HUGO_DIR=

# Remove current docs in sdk_docs_temp
rm -rf $TEMP_DIR/*.md

# Generate SDK docs using lazydocs
python generate_sdk_docs.py --temp_output_directory=$TEMP_DIR

# Process output doc created by lazydocs so it works with Docusaurus
python process_sdk_markdown.py --output_directory=$TEMP_DIR

# Make destination directory
mkdir -p $DESTINATION_DIR

# Rename README.md to _index.md
mv $TEMP_DIR/README.md $HUGO_DIR/$DESTINATION_DIR/_index.md

# Create subdirectories based on API or DataType
python transfer_files.py --source_directory=$TEMP_DIR --destination_directory=$DESTINATION_DIR

# Move files to Hugo directory
mv $DESTINATION_DIR $HUGO_DIR