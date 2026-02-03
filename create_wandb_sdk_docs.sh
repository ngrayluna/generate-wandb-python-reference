#!/bin/bash

TEMP_DIR=wandb_sdk_docs
DESTINATION_DIR=python
JSON_OUTPUT_DIR=logs

# Copy docs.json from docs/ repo to current directory
PARENT_DOCS_DIR="../docs"
DOCS_JSON_FILE="$PARENT_DOCS_DIR/docs.json"

# Check if the directory exists, if it does, remove it else create it
if [ -d "$TEMP_DIR" ]; then
  echo "Directory '$TEMP_DIR' already exists. Removing it."
  rm -rf "$TEMP_DIR"
else
  echo "Directory '$TEMP_DIR' does not exist. Creating it."
  mkdir -p "$TEMP_DIR"
fi

# Check if the destination directory exists, if it does, remove it else create it
if [ -d "$DESTINATION_DIR" ]; then
  echo "Directory '$DESTINATION_DIR' already exists. Removing it."
  rm -rf "$DESTINATION_DIR"
else
  echo "Directory '$DESTINATION_DIR' does not exist. Creating it."
  mkdir -p "$DESTINATION_DIR"
fi

# Check if the destination directory exists, if it does, remove it else create it
if [ -d "$JSON_OUTPUT_DIR" ]; then
  echo "Directory '$JSON_OUTPUT_DIR' already exists. Removing it."
  rm -rf "$JSON_OUTPUT_DIR"
else
  echo "Directory '$JSON_OUTPUT_DIR' does not exist. Creating it."
  mkdir -p "$JSON_OUTPUT_DIR"
fi

# Generate SDK docs using lazydocs
python generate_sdk_docs.py --temp_output_directory=$TEMP_DIR

# Process output doc created by lazydocs so it works with Docusaurus
python process_sdk_markdown.py --markdown_directory=$TEMP_DIR

# Make destination directory
mkdir -p $DESTINATION_DIR

# Sort and create subdirectories based on API or DataType
python sort_markdown_files.py --source_directory=$TEMP_DIR --destination_directory=$DESTINATION_DIR

# Clean up the directory: add admonitions, extract mdx files, etc.
python cleanup_directory.py --directory=$DESTINATION_DIR --json-output=$JSON_OUTPUT_DIR

if [ -d "$PARENT_DOCS_DIR" ]; then
  echo "Found '$PARENT_DOCS_DIR' directory."
  if [ -f "$DOCS_JSON_FILE" ]; then
    echo "Copying docs.json to current directory..."
    cp "$DOCS_JSON_FILE" .
    echo "Done. docs.json copied successfully."
  else
    echo "Error: docs.json not found in '$PARENT_DOCS_DIR'."
    exit 1
  fi
else
  echo "Error: '$PARENT_DOCS_DIR' directory does not exist."
  exit 1
fi

# Compare generated .mdx files with docs.json
python check_mdx_vs_docsjson.py --mdx-list=$JSON_OUTPUT_DIR/mdx_file_list.json \
  --docs-json=$DOCS_JSON_FILE \
  --output-report-dir=$JSON_OUTPUT_DIR