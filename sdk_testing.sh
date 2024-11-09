#!/bin/bash


TEMP_DIR=sdk_docs_temp

# Generate SDK docs using lazydocs
python generate_sdk_docs.py 

# Process output doc created by lazydocs so it works with Docusaurus
python process_sdk_markdown.py --output_directory=$TEMP_DIR

# Copy processed markdown files to docodile
cp $TEMP_DIR/*.md /Users/noahluna/Desktop/docodile/docs/ref/lazy_docs_python