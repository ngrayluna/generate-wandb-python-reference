#! /bin/usr/python
import os
import re
import inspect

import wandb 
import lazydocs

# TO DO: import this from pyi
__all__ = (
    "__version__",
    "init",
    "finish",
    "setup",
    "login",
    "save",
    "sweep",
    "controller",
    "agent",
    "config",
    "log",
    "summary",
    "Api",
    "Graph",
    "Image",
    "Plotly",
    "Video",
    "Audio",
    "Table",
    "Html",
    "box3d",
    "Object3D",
    "Molecule",
    "Histogram",
    "ArtifactTTL",
    "log_artifact",
    "use_artifact",
    "log_model",
    "use_model",
    "link_model",
    "define_metric",
    "Error",
    "termsetup",
    "termlog",
    "termerror",
    "termwarn",
    "Artifact",
    "Settings",
    "teardown",
    "watch",
    "unwatch",
)


def create_public_api_list(module):
    # Remove any from list that are supposed to be hidden
    dir_output = [name for name in dir(module) if not name.startswith('_')]

    # Return alphabetize the list
    return sorted(list(set(dir_output) and set(__all__)))    


def _github_button(href_links):
    """To do: Add hugo scripting to add this function. For now, just add code line # for debugging."""
    return href_links + "\n\n"

def format_github_button(filename, base_url="https://github.com/wandb/wandb/blob/main/wandb"):
    """Add GitHub button to the markdown file."""

    def _extract_filename_from_path(path: str) -> str:
        # Only get path after "wandb/" in the URL
        _, _, wandb_path = path.partition("wandb/")
        return wandb_path

    href_links = os.path.join(base_url, _extract_filename_from_path(filename))
    return _github_button(href_links)


def add_frontmatter(filename):
    """Add frontmatter to the markdown file."""
    base_name = os.path.basename(filename).split('.')[0]
    return f"---\ntitle: {base_name}\n---\n\n"


def create_class_markdown(obj, module, generator, filename):
    with open(filename, 'w') as file:
        file.write(add_frontmatter(filename))
        file.write(format_github_button(inspect.getfile(obj)))        
        file.write("\n\n")
        # file.write( 'source code line ' +  str(inspect.getsourcelines(obj)[1])) # In the future, add this to the markdown file
        file.write(generator.class2md(obj))

def create_function_markdown(obj, module, generator, filename):
    with open(filename, 'w') as file:
        file.write(add_frontmatter(filename))
        file.write(format_github_button(inspect.getfile(obj)))
        file.write("\n\n")
        # file.write( 'source code line ' +  str(inspect.getsourcelines(obj)[1])) # In the future, add this to the markdown file
        file.write(generator.func2md(obj))

def _check_temp_dir():
    # Check if temporary directory exists
    if not os.path.exists('sdk_docs_temp/'):
        os.makedirs('sdk_docs_temp/')

def get_output_markdown_path(api_list_item):
    # Store generated files in sdk_docs_temp directory
    # This directory is used by process_sdk_markdown.py
    _check_temp_dir()

    filename = api_list_item + '.md'
    return os.path.join(os.getcwd(), 'sdk_docs_temp/', filename)

def create_markdown(api_list_item, module, src_base_url):
    # Create output filepath
    filename = get_output_markdown_path(api_list_item)

    # Get object from module
    obj = getattr(module, api_list_item)
    
    # Get generator object
    generator = lazydocs.MarkdownGenerator(src_base_url=src_base_url)

    # Check if object is a class or function
    if str(type(obj)) == "<class 'type'>":
        print(f"Generating docs for {obj} class")
        create_class_markdown(obj, module, generator, filename=filename)
    elif str(type(obj)) == "<class 'function'>":
        print(f"Generating docs for {obj} function")
        create_function_markdown(obj, module, generator, filename=filename)
    else:
        print(f"Skipping {obj}")    


def main():
    module = wandb
    src_base_url = "https://github.com/wandb/wandb/tree/main/"
    
    # Get list of public APIs
    api_list = create_public_api_list(module)

    # To do: Get api_list from module
    for api in api_list:
        create_markdown(api, module, src_base_url)

if __name__  == "__main__":
    main()