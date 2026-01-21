#!/bin/usr/bash

MODULE1=wandb_workspaces.workspaces.interface
MODULE2=wandb_workspaces.reports.v2.interface
OUTPUT_DIR=wandb_workspaces


if [ -d "$OUTPUT_DIR" ]; then
    echo "Workspace and Reports directory exists"
else
    echo "Workspace and Reports directory does not exist. Creating it now..."
    mkdir -p "$OUTPUT_DIR"
    echo "Directory created: $OUTPUT_DIR"
fi

## Array of modules to process
declare -a arr=($MODULE1 $MODULE2)

# Create initial doc for each module
for MODULE in "${arr[@]}"
do  
    echo "Generating docs for module: $MODULE"
    lazydocs --output-path=./$OUTPUT_DIR $MODULE --src-base-url="https://github.com/wandb/wandb-workspaces/tree/main"

    echo "Processing markdown files for module: $OUTPUT_DIR/$MODULE.md"
    python process_sdk_markdown.py --markdown_directory $OUTPUT_DIR

    echo "Mintlify docs..."
    # Clean up the directory: add admonitions, extract mdx files, etc.
    python mintlify_workspaces_report_docs.py --markdown_directory $OUTPUT_DIR
done