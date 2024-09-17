#!/bin/usr

MODULE=wandb_workspaces.workspaces.interface
# MODULE=wandb_workspaces.reports.v2.interface
TMP_DIR=workspaces_tmp
DIR="/Users/noahluna/Desktop/docodile/docs/ref/wandb_workspaces/"


lazydocs --output-path=./$TMP_DIR $MODULE


python post_process_markdown.py $TMP_DIR/$MODULE.md 
# python post_process_markdown.py $TMP_DIR/wandb_workspaces.reports.v2.interface.md


# FUTURE: Create README
## Get file name file e.g. wandb_workspaces.workspaces.interface.md
## Extract worskpace
## Add that as a line in README and link to it?


if [ -d "$DIR" ]; then
    echo "Directory exists"
else
    echo "Directory does not exist. Creating it now..."
    mkdir -p "$DIR"
    echo "Directory created: $DIR"
fi



# Move contents
cp ./$TMP_DIR/* $DIR

# Clean up
# rm ./$TMP_DIR


