#!/bin/usr

# FUTURE: Create README
## Get file name file e.g. wandb_workspaces.workspaces.interface.md
## Extract worskpace
## Add that as a line in README and link to it?

# MODULE=wandb_workspaces.workspaces.interface
MODULE=wandb_workspaces.reports.v2.interface
TMP_DIR=workspaces_tmp
DIR="/Users/noahluna/Desktop/docodile/docs/ref/python/workspaces/"

# Create initial doc
lazydocs --output-path=./$TMP_DIR $MODULE --src-base-url="https://github.com/wandb/wandb-workspaces/tree/main"

# Process output of doc created by lazydocs so it works with Docusaurus
python post_process_markdown.py $TMP_DIR/$MODULE.md 

# Check that directory exists in docodile/docs/ref/, if not, create one
if [ -d "$DIR" ]; then
    echo "Directory exists"
else
    echo "Directory does not exist. Creating it now..."
    mkdir -p "$DIR"
    echo "Directory created: $DIR"
fi

# Move contents from TMP DIR to docodile
cp ./$TMP_DIR/* $DIR

# Clean up
# rm ./$TMP_DIR


