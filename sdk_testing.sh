#!/bin/bash


TEMP_DIR=sdk_docs_temp

python generate_sdk_docs.py 

python process_sdk_markdown.py --output_directory=$TEMP_DIR

cp $TEMP_DIR/*.md /Users/noahluna/Desktop/docodile/docs/ref/lazy_docs_python