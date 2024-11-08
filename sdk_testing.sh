#!/bin/bash


python generate_sdk_docs.py 

python process_sdk_markdown.py Artifact.md


#cp Artifact.md /Users/noahluna/Desktop/docodile/docs/ref/lazy_docs_python