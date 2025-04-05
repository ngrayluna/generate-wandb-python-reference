#!/bin/usr/python
import os
import argparse

page_content = {
    "public-api": {
        "title": "Analytics and Query API",
        "description": "Query and analyze data logged to W&B.",
    },
    "data-type": {
        "title": "Data Types",
        "description": "Defines Data Types for logging interactive visualizations to W&B.",
    },
    "actions": {
        "title": "SDK",
        "description": "Use during training to log experiments, track metrics, and save model artifacts.",
    },
    "launch-library": {
        "title": "Launch Library",
        "description": "A collection of launch APIs for W&B.",
    }
}


def create_markdown_index_page(root_directory):
    """Create an _index.md file for each directory in the root directory for testing purposes.
    
    Checks if the directory contains an _index.md file. If not,
    creates one based on the directory name and predefined page content.

    Args:
        root_directory (str): The root directory to search for _index.md files.
    """
    for dirpath, dirnames, filenames in os.walk(root_directory):
        if '_index.md' not in filenames:
            if dirpath ==  "python-library":
                create_python_index_file(dirpath)
                continue
            
            dir_name = os.path.basename(dirpath)
            if dir_name in page_content:
                new_title = page_content[dir_name]["title"]
                description = page_content[dir_name]["description"]
            else:
                new_title = dir_name.replace("-", " ").replace("_", " ").title()
                description = "No description available."

            index_file = os.path.join(dirpath, "_index.md")
            with open(index_file, 'w') as file:
                file.write("---\ntitle: " + new_title + "\n---\n")
                file.write(description + "\n")
            print(f"Created {index_file}\n")
    return


def create_python_index_file(filepath):
    """Create an _index.md file for the top most python-library folder."""

    # Create _index.md and add header
    index_file = os.path.join(filepath, "_index.md")

    # Title to print on the top most directory
    title = "Python"

    cardpane = """{{< cardpane >}}
    {{< card >}}
        <a href="/ref/python-library/actions">
        <h2 className="card-title">SDK</h2>
        <p className="card-content">Use during training to log experiments, track metrics, and save model artifacts.</p>
        </a>
    {{< /card >}}
    {{< card >}}
        <a href="/ref/python-library/data-types">
        <h2 className="card-title">Data Types</h2>
        <p className="card-content">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
        </a>
    {{< /card >}}
    {{< /cardpane >}}
    {{< cardpane >}}
    {{< card >}}
        <a href="/ref/python-library/public-api">
        <h2 className="card-title">Analytics and Query API</h2>
        <p className="card-content">Query and analyze data logged to W&B.</p>
        </a>
    {{< /card >}}
    {{< card >}}
        <a href="/ref/python-library/launch-library">
        <h2 className="card-title">Launch Library</h2>
        <p className="card-content">A collection of launch APIs for W&B.</p>
        </a>
    {{< /card >}}
    {{< /cardpane >}}"""

    with open(index_file, 'w') as file:
        file.write("---\ntitle: " + title + "\n---\n")
        file.write(cardpane)
     
    print(f"Created {index_file}\n")
    return


def main(args):
    print("\nChecking for _index.md files...")
    create_markdown_index_page(args.source_directory)  # For testing purposes

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory", default="python-library", help="directory where the markdown exist")
    args = parser.parse_args()
    main(args)