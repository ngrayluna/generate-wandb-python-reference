#!/bin/bash


python generate_sdk_docs.py 

python process_sdk_markdown.py --output_directory="sdk_docs_temp"


#cp Artifact.md /Users/noahluna/Desktop/docodile/docs/ref/lazy_docs_python