#!/bin/bash

TEMP_DIR=wandb_sdk_docs
TEMP_IMPORT_EXPORT_DIR=wandb_import_export_docs
DESTINATION_DIR=python-library
HUGO_DIR=/Users/noahluna/Desktop/RandomProjects/docs/content/ref/

# Remove current docs in sdk_docs_temp
rm -rf $TEMP_DIR/*.md

# Remove current docs in Hugo directory
rm -rf $HUGO_DIR/$DESTINATION_DIR

# Generate SDK docs using lazydocs
python generate_sdk_docs.py --temp_output_directory=$TEMP_DIR

# Process output doc created by lazydocs so it works with Docusaurus
python process_sdk_markdown.py --output_directory=$TEMP_DIR

# Make destination directory
mkdir -p $DESTINATION_DIR

# Sort and create subdirectories based on API or DataType
python sort_files.py --source_directory=$TEMP_DIR --destination_directory=$DESTINATION_DIR

# Create _index.md files
python create_landing_pages.py --source_directory=$DESTINATION_DIR

# Move local file with subdirs to Hugo directory
#echo "Moving files to Hugo directory"
mv $DESTINATION_DIR $HUGO_DIR

# TO DO: Clean this up
# Rename README.md to _index.md and move to Hugo directory
# echo "Moving _index.md"
# mv $TEMP_DIR/README.md $TEMP_DIR/_index.md 
# mv $TEMP_DIR/_index.md $HUGO_DIR/$DESTINATION_DIR