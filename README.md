# Generate W&B Python SDK with `lazydocs`

Scripts that generated markdown docs for Workspaces API and broader W&B Python API documentation.

## Setup
1. Navigate to the root directory that contains your local clone of the `wandb` repository. This is the directory that contains the `wandb` package.

   ```bash
   cd path/to/your/root/directory/with/wandb/package
   ```
2. Clone `generate-wandb-python-reference` repository:

   ```bash
   git clone https://github.com/user-attachments/generate-wandb-python-reference.git
   ```

    Your local directory structure should look like this:

    ```text
    awesome-directory/
    ├── generate-wandb-python-reference/
    │   ├── create_wandb_sdk_docs.sh
    │   ├── generate_sdk_docs.py
    │   ├── process_markdown.py
    │   ├── sort_markdown_files.py
    │   ├── create_landing_pages.py
    │   ├── requirements.txt
    │   └── configuration.py
    └── wandb/
        ├── wandb/
        │   ├── __init__.py
        │   ├── __init__.template.pyi
        │   └── ... # other files
        └──
    ```

3. Install the required dependencies:
   ```bash
   cd generate-wandb-python-reference
   pip install -r requirements.txt
   ``` 

## Create W&B Python SDK Docs

These scripts use the local cloned version of `wandb` package to generate the markdown files. (This is why you need to clone the `generate-wandb-python-reference` repository into the same directory as your local `wandb` package.)

Check out the branch or commit that you want to generate the docs for.

```bash title="wandb"
git checkout <branch-or-commit>
```

The entrypoint for generating the W&B Python SDK docs is the `generate-wandb-python-reference/create_wandb_sdk_docs.sh` script.

```bash title="generate-wandb-python-reference"
bash create_wandb_sdk_docs.sh
```

The output will be generated in the `wandb/wandb/docs/python` directory. The generated markdown files will be organized into subdirectories based on the `object_type` specified in the front matter of each markdown file.

## Overview of the scripts
The script does the following, in this order:

1. Call `generate_sdk_docs.py` script to generate markdown docs using `lazydocs`. The script uses Classes, functions, and W&B Data Types from `wandb/wandb/__init__.pyi` file.
2. Call `process_markdown.py` script to process the markdown docs generated by `lazydocs`. Namely, the processing script removes weird artifacts that `lazydocs` generates and adds the necessary front matter to the markdown files that Hugo requires.
3. Call `sort_markdown_files.py` to reorganize the markdown files into the correct directory structure for the W&B Python docs. It reads in the front matter of processed markdown files (processed by `process_ask_markdown.py`) and, based on the value specified for `object_type`, move files to "data-types", "launch-library", etc. directories.
4. Call `create_landing_pages.py` to generate the `_index.md` files


## How to add your APIs to the reference docs

Start off by asking yourself: Is the API you defined already in an existing namespace? E.g. `wandb.sdk`, `wandb.apis.public`, or `wandb.sdk.launch`. For a full list, see the "module" keys specifed in `configuration.py`.

If yes, then:

1. Add your new APIs to the `__all__` contsant within the appropriate `__init__.py` or `__init__.template.pyi` file. See  `wandb/wandb/__init__.template.pyi` for an example.
2. Add `# doc:exclude` next to the name of any API that you do not want to publicly expose. 
 

If no, then:

1. Open `configuration.py`
2. Add a new entry to the SOURCE dictionary. Here is a template for reference:
   ```yaml
    "API_NAME": {
        "module": "", # The module that contains your code
        "file_path": "", # File path of the local wandb/wandb source files
        "hugo_specs": {
            "title": "", # Title of the folder (What appears in the left navigation)
            "description": "", # Description of the top most _index.md file
            "frontmatter": "object_type: ", # frontmatter, used for sorting
            "folder_name": "", # Desired directory within python E.g. python/launch-library, python/data-type/
        }
    }
   ```


