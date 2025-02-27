#!/bin/usr/python
import os
import argparse

def create_landing_page(root_directory):

    # Check if the directory exists
    for dirpath, dirnames, filenames in os.walk(root_directory):
        if '_index.md' not in filenames:
            if dirpath == "python-library":
                create_python_index_file(dirpath)
                continue
            elif "data_types" in dirpath:
                create_data_type_index_file(dirpath)
                continue
            elif "actions" in dirpath:
                create_actions_index_file(dirpath)
                continue
            else:
                create_generic_index_file(dirpath)
    return

def create_python_index_file(filepath):
    """Create an index file for the python-library directory."""

    # Create _index.md and add header
    index_file = os.path.join(filepath, "_index.md")

    # Create title from directory name
    new_title = os.path.basename(filepath).replace("-", " ").replace("_", " ").title()

    cardpane = """{{< cardpane >}}
    {{< card >}}
        <a href="/ref/python-library/actions">
        <h2 className="card-title">Actions</h2>
        <p className="card-content">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
        </a>
    {{< /card >}}
    {{< card >}}
        <a href="/ref/python-library/data_types">
        <h2 className="card-title">Data Types</h2>
        <p className="card-content">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
        </a>
    {{< /card >}}
    {{< /cardpane >}}"""

    with open(index_file, 'w') as file:
        file.write("---\ntitle: " + new_title + "\n---\n")
        file.write(cardpane)

        
    print(f"Created {index_file}\n")
    return


def create_data_type_index_file(filepath):
    """Create an index file for the data_types directory."""

    sentence_1 = """This module defines Data Types for logging interactive visualizations to W&B. 
    Data types include common media types, like images, audio, and videos, flexible containers 
    for information, like tables and HTML, and more. All of these special data types are subclasses
    of WBValue. All the data types serialize to JSON, since that is what wandb uses to save
    the objects locally and upload them to the W&B server."""

    sentence_2 = """For more on logging media, see our guide. For more on logging
    structured data for interactive dataset and model analysis, see to W&B Tables."""

    # Create _index.md and add header
    index_file = os.path.join(filepath, "_index.md")

    # Create title from directory name
    new_title = os.path.basename(filepath).replace("-", " ").replace("_", " ").title()

    with open(index_file, 'w') as file:
        file.write("---\ntitle: " + new_title + "\n---\n")
        file.write(sentence_1 + "\n\n")
        file.write(sentence_2 + "\n")
    print(f"Created {index_file}\n")
    return

def create_actions_index_file(filepath):
    """Create an index file for the actions directory."""

    sentence_1 = """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
    ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit
    in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur
    sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt
    mollit anim id est laborum."""

    # Create _index.md and add header
    index_file = os.path.join(filepath, "_index.md")

    # Create title from directory name
    new_title = os.path.basename(filepath).replace("-", " ").replace("_", " ").title()

    with open(index_file, 'w') as file:
        file.write("---\ntitle: " + new_title + "\n---\n")
        file.write(sentence_1 + "\n\n")
    print(f"Created {index_file}\n")
    return


def create_generic_index_file(filepath):
    """Create an index file for a generic directory."""

    # Create _index.md and add header
    index_file = os.path.join(filepath, "_index.md")

    # Create title from directory name
    new_title = os.path.basename(filepath).replace("-", " ").replace("_", " ").title()

    with open(index_file, 'w') as file:
        file.write("---\ntitle: " + new_title + "\n---\n")
    print(f"Created {index_file}\n")
    return



def main(args):
    print("\nCreating landing pages for SDK docs...\n")
    create_landing_page(args.source_directory)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory", default="python-library", help="directory where the markdown exist")
    args = parser.parse_args()
    main(args)