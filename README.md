# Generate W&B Python SDK with `lazydocs`

Scripts that generate markdown files for W&B Python SDK.

## Setup
Navigate to a directory where you want to clone both the `wandb` repository and the `generate-wandb-python-reference` repository. For example, suppose you create a directory called `awesome-directory` as the root directory:

1. Create and navigate to your working directory:
   ```bash
   mkdir awesome-directory
   cd awesome-directory
   ```

2. Clone the `wandb` repository locally if you haven't already:

   ```bash
   git clone https://github.com/wandb/wandb.git
   ```

3. Navigate back to the parent directory (in this case `awesome-directory`) and clone the `generate-wandb-python-reference` repository:

   ```bash
   cd ../
   git clone https://github.com/ngrayluna/generate-wandb-python-reference.git
   ```

> The previous examples clone repos using `https`. Consider using a password-protected SSH remote URL instead.

Your local directory structure should look like this:

```text
awesome-directory/
├── generate-wandb-python-reference/
│   ├── create_wandb_sdk_docs.sh
│   ├── generate_sdk_docs.py
│   ├── process_markdown.py
│   ├── sort_markdown_files.py
│   ├── requirements.txt
│   └── configuration.py
└── wandb/
   ├── wandb/
   │   ├── __init__.py
   │   ├── __init__.template.pyi
   │   └── ... # other files
   └──
```

4. Install the required dependencies:
   ```bash
   cd generate-wandb-python-reference
   pip install -r requirements.txt
   ``` 

5. (Optionally) Install the [W&B Docs](https://github.com/wandb/docs) repo in the root directory. Continuing from the previous example:
   ```bash
   cd awesome-directory
   git clone https://github.com/wandb/docs.git
   ```
   Your directory should look similar to the following:

   ```text
   awesome-directory/
   ├── generate-wandb-python-reference/
   │   ├── create_wandb_sdk_docs.sh
   │   ├── generate_sdk_docs.py
   │   ├── process_markdown.py
   │   ├── sort_markdown_files.py
   │   ├── requirements.txt
   │   └── configuration.py
   └── wandb/
   |   ├── wandb/
   |   │   ├── __init__.py
   |   │   ├── __init__.template.pyi
   |   │   └── ... # other files
   |   └──
   └── docs/
      ├── docs.json
      └── ... # other files
   ```

## Create W&B Python SDK Docs

These scripts use the local cloned version of `wandb` package to generate the markdown files. (This is why you need to clone the `generate-wandb-python-reference` repository into the same directory as your local `wandb` package.)

Check out the branch or commit that you want to generate the docs for.

```bash title="wandb"
cd wandb/
git fetch --tags
git checkout <tag-or-commit-hash>
```

> Note: You can also use a specific tag instead of a commit hash. This is useful if you want to generate docs for a specific release.

For example, to generate docs for the `v0.23.0` release:

```bash title="wandb"
cd wandb/
git fetch --tags
git checkout v0.23.0
```

The entrypoint for generating the W&B Python SDK docs is the `generate-wandb-python-reference/create_wandb_sdk_docs.sh` script.

```bash title="generate-wandb-python-reference"
cd ../generate-wandb-python-reference/
bash create_wandb_sdk_docs.sh
```

The output will be generated in the `wandb/wandb/docs/python` directory. The generated markdown files will be organized into subdirectories based on the `object_type` specified in the front matter of each markdown file.

#### Optional flag: `--check-docs-json`

The `docs.json` file in the [W&B Docs](https://github.com/wandb/docs) repository defines the sidebar navigation structure for the documentation site. Each `.mdx` file must be referenced in `docs.json` to appear in the sidebar.

Use the `--check-docs-json` flag to verify that all generated `.mdx` files are properly referenced in `docs.json`:

```bash
bash create_wandb_sdk_docs.sh --check-docs-json
```

This flag:
1. Copies `docs.json` from the parent `docs/` directory to the current directory
2. Runs `check_mdx_vs_docsjson.py` to compare generated `.mdx` files against `docs.json`

The check helps identify:
- New `.mdx` files that need to be added to `docs.json`
- Stale references in `docs.json` pointing to files that no longer exist

By default, this check is skipped. Use this flag when you want to ensure the generated documentation will integrate correctly with the docs site navigation.

## Add new W&B Python objects to the reference docs

```
                    ┌─────────────────────────────────────┐
                    │  Add new Python object to docs      │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  Is the object in an existing       │
                    │  namespace?                         │
                    │                                     │
                    │  Existing namespaces:               │
                    │  • wandb (SDK/Actions)              │
                    │  • wandb.plot (Custom Charts)       │
                    │  • wandb.sdk.data_types (Data Types)│
                    │  • wandb.apis.public (Query API)    │
                    │  • wandb.automations (Automations)  │
                    └─────────────────┬───────────────────┘
                                      │
                     ┌────────────────┴────────────────┐
                     │                                 │
                    YES                               NO
                     │                                 │
                     ▼                                 ▼
    ┌────────────────────────────────┐   ┌────────────────────────────────┐
    │  1. Add to `__all__` in the    │   │  1. Open configuration.py      │
    │     appropriate file:          │   │                                │
    │     • __init__.py              │   │  2. Add new entry to SOURCE    │
    │     • __init__.template.pyi    │   │     dictionary with:           │
    │                                │   │     • module                   │
    │  2. Add ignore markers to      │   │     • file_path                │
    │     exclude internal items     │   │     • hugo_specs:              │
    │     (if needed)                │   │       - title                  │
    └────────────────┬───────────────┘   │       - description            │
                     │                   │       - frontmatter            │
                     │                   │       - folder_name            │
                     │                   └────────────────┬───────────────┘
                     │                                    │
                     └────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  Run: bash create_wandb_sdk_docs.sh │
                    └─────────────────────────────────────┘
```

First, ask yourself: Is the Python object already in an existing namespace? E.g. `wandb`, `wandb.apis.public`, or `wandb.automations`.

> [See the `"module"` keys](https://github.com/ngrayluna/generate-wandb-python-reference/blob/main/configuration.py#L5) specified in `configuration.py` for a full list of existing namespaces.

If yes, then:

1. Add your new APIs to the `__all__` contsant within the appropriate `__init__.py` or `__init__.template.pyi` file. See  `wandb/wandb/__init__.template.pyi` for an example.
2. If there is a class, class method, function, etc. that SHOULD NOT be publically documented, add an [ignore marker](#ignore-markers) to the docstring of that class, method, etc. For example:
   ```python
   class MyClass:
       """This is an awesome Python Class.

       <!-- lazydoc-ignore-class: internal -->
       """
       def my_method(self):
           """This is an awesome method."""
           pass
   ```

   See the [ignore markers](#ignore-markers) section for more details on how to use ignore markers.
 
If no, then:

1. Open `configuration.py`
2. Add a new entry to the SOURCE dictionary. Here is a template for reference:
   ```yaml
    "API_NAME": {
        "module": "", # The module that contains your code (e.g. wandb.apis.public)
        "file_path": "", # File path of the local wandb/wandb source files
        "hugo_specs": {
            "title": "", # Title of the folder (What appears in the left navigation)
            "description": "", # Description of the top most _index.md file
            "frontmatter": "object_type: ", # frontmatter, used for sorting
            "folder_name": "", # Desired directory within python E.g. python/launch-library, python/data-type/
        }
    }
   ```

For `file_path`, use the variable BASE_DIR as a prefix. For example, for `wandb.apis.public`, the file path would look like this:

```py
"file_path": BASE_DIR / "wandb" / "wandb" / "apis" / "public" / "__init__.py"
```

### Ignore markers

To exclude certain classes, methods, or functions from the documentation generated by `lazydocs`, you can use the following ignore markers in your code:

1. `<!-- lazydoc-ignore: internal -->` - Removes internal class method definitions
2. `<!-- lazydoc-ignore-class: internal -->` - Removes entire class definitions
3. `<!-- lazydoc-ignore-function: internal -->` - Removes function definitions
4. `<!-- lazydoc-ignore-classmethod: internal -->` - Removes `@classmethod` definitions
5. `<!-- lazydoc-ignore-init: internal -->` - Removes `__init__` method definitions
6. `<!-- lazydoc-ignore-class-attributes -->` - Removes individual attribute bullet points

> Why does ignore markers exist?
> * There are internal classes, methods, properties, etc. in the Python SDK that are not meant to be publicly exposed and do not use the Python convention of preprending a single underscore (`_`) to indicate that they are private.
> * `lazydocs` is a generic tool that generates documentation for any Python code, it may include some artifacts that are not relevant to the W&B Python SDK.


## Documentation pipeline
`create_wandb_sdk_docs.sh` follows a 4-step process to generate the W&B Python SDK documentation:

1. **`generate_sdk_docs.py`**: Generates initial markdown documentation using `lazydocs`
   - Parses W&B Python SDK modules defined in `configuration.py`
   - Extracts classes, functions, and data types from `__init__.py` and `__init__.template.pyi` files
   - Handles Pydantic models with custom Google-style docstring generation
   - Generates GitHub source links for each documented object
   - Outputs to temporary directory `/wandb_sdk_docs/`

2. **`process_sdk_markdown.py`**: Cleans and enhances markdown artifacts
   - Removes HTML tags and lazydocs-specific formatting artifacts
   - Processes ignore markers to exclude internal/private APIs.
   - Reorders class documentation (moves `__init__` before Args section)
   - Removes "Global Variables" sections

3. **`sort_markdown_files.py`**: Organizes files into directory structure
   - Reads frontmatter from processed markdown files
   - Routes files to appropriate subdirectories based on `namespace` field
   - Creates `/functions/` and `/experiments/` subdirectories for SDK items
   - Organizes files according to `configuration.py` folder mappings

4. **`cleanup_directory.py`**: Final cleanup and enhancements
   - Removes `_wandb` suffixes from filenames (added by lazydocs to avoid conflicts)
   - Updates titles in frontmatter to remove `_wandb` suffixes
   - Handles duplicate files by comparing frontmatter metadata
   - Adds public API admonitions to files in `/public-api/` directory
   - Deletes empty directories


### Configuration
- **`configuration.py`**: Central configuration defining all documentation sources
  - Maps Python modules to their source locations
  - Specifies output directory structure and organization rules
