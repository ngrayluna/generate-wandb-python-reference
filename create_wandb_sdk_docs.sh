#!/bin/bash

TEMP_DIR=wandb_sdk_docs
DESTINATION_DIR=python-library
### HUGO_DIR=/Users/noahluna/Desktop/docs/content/ref/
#HUGO_DIR=/Users/noahluna/Desktop/staging/ref/


# Check if the script is run from the correct directory
if [ ! -d "$TEMP_DIR" ]; then
  mkdir -p "$TEMP_DIR"
  echo "Directory '$TEMP_DIR' created."
else
  echo "Directory '$TEMP_DIR' already exists."
fi

# Check if the destination directory exists, if not, create it
if [ ! -d "$DESTINATION_DIR" ]; then
  mkdir -p "$DESTINATION_DIR"
  echo "Directory '$DESTINATION_DIR' created."
else
  echo "Directory '$DESTINATION_DIR' already exists."
fi


# # Remove current docs in sdk_docs_temp
# rm -rf $TEMP_DIR/*.md

# # Remove current docs in Hugo directory
# rm -rf $HUGO_DIR/$DESTINATION_DIR

# Generate SDK docs using lazydocs
python generate_sdk_docs.py --temp_output_directory=$TEMP_DIR

# Process output doc created by lazydocs so it works with Docusaurus
python process_sdk_markdown.py --output_directory=$TEMP_DIR

# Make destination directory
mkdir -p $DESTINATION_DIR

# Sort and create subdirectories based on API or DataType
python sort_markdown_files.py --source_directory=$TEMP_DIR --destination_directory=$DESTINATION_DIR

# Create _index.md files
python create_landing_pages.py --source_directory=$DESTINATION_DIR

# Move local file with subdirs to Hugo directory
#echo "Moving files to Hugo directory"
#mv $DESTINATION_DIR $HUGO_DIR