#!/bin/bash

TEMP_DIR=wandb_sdk_docs
SRC=python-library
DEST=/Users/noahluna/Desktop/RandomProjects/docs/content/ref/

# Remove current docs in sdk_docs_temp
rm -rf $TEMP_DIR/*.md

# Remove output directory if it exists
if [ -d "$SRC" ]; then
    rm -rf $SRC
fi

# Remove current docs in Hugo directory
#rm -rf $DEST/$SRC

# Generate SDK docs using lazydocs
python generate_sdk_docs.py --temp_output_directory=$TEMP_DIR

# Process output doc created by lazydocs so it works with Docusaurus
python process_sdk_markdown.py --output_directory=$TEMP_DIR

# Make destination directory
mkdir -p $SRC

# Sort and create subdirectories based on API or DataType
python sort_markdown_files.py --source_directory=$TEMP_DIR --destination_directory=$SRC

# Create _index.md files
python create_landing_pages.py --source_directory=$SRC

# Move local file with subdirs to Hugo directory
#echo "Moving files to Hugo directory"
#mv $SRC $DEST

# TO DO: Clean this up
# Rename README.md to _index.md and move to Hugo directory
# echo "Moving _index.md"
# mv $TEMP_DIR/README.md $TEMP_DIR/_index.md 
# mv $TEMP_DIR/_index.md $HUGO_DIR/$DESTINATION_DIR

# Step 1: Rsync everything EXCEPT _index.md at any depth
rsync -a --filter='- **/_index.md' "$SRC" "$DEST"

# Step 2: Manually copy _index.md files ONLY where they don't already exist
find "$SRC" -type f -name '_index.md' | while read -r src_file; do
    # Compute relative path from folderA
    rel_path="${src_file#$SRC/}"
    dest_file="$DEST/$(basename "$SRC")/$rel_path"

    if [[ ! -f "$dest_file" ]]; then
        mkdir -p "$(dirname "$dest_file")"
        cp "$src_file" "$dest_file"
    fi
done