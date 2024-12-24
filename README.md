# Generate W&B Pytyhon SDK

Scripts that generated markdown docs for Workspaces API and broader W&B Python API documentation.

## Create W&B Python SDK Docs

The entrypoint for generating the W&B Python SDK docs is the `create_wandb_sdk_docs.sh` script. 

```bash
bash create_wandb_sdk_docs.sh
```

The script does the following:

1. Call `new_sdk_docs.py` script to generate markdown docs using `lazydocs`. The script uses Classes, functions, and W&B Data Types from `wandb/wandb/__init__.pyi` file.
2. Call `process_markdown.py` script to process the markdown docs generated by lazydocs. Namely, the processing script removes weird artifacts that lazydocs generates and adds the necessary front matter to the markdown files that Hugo requires.
3. Call `transfer_files.py` to reorganize the markdown files into the correct directory structure for the W&B Python SDK docs. It reads in the front matter of processed markdown files (processed by `process_markdown.py`) and, based on the value specified for `object_type`, move files to either a "data_types" or "api" directory.


## Add new APIs or Data Types to the SDK Reference Docs

Add new APIs or Data Types to the constant `__all__` within `wandb/wandb/__init__.template.pyi` file. The `new_sdk_docs.py` script reads in `wandb/wandb/__init__.pyi` file to generate markdown docs.

Add `#docs:exclude` next to the name of any API or Data Class that is should not be public facing. This will exclude the API or Data Class from the generated markdown docs.
 

## Test markdown files locally

Within `new_sdk_docs.py`, uncomment out the code snippet specified in the `USE LOCAL VERSION` comment. This will use the local version of the `wandb` package to generate the markdown docs. 

Ensure to specify the path of your local `wandb` package for:

```python titile="new_sdk_docs.py"
local_wandb_path = Path("path/to/local/wandb")
```
