#!/usr/bin/env python

import os
import argparse
import wandb

from configuration import SOURCE


def build_page_content_from_source():
    """Construct page content from the SOURCE Python file."""
    content = {}
    for value in SOURCE.values():
        module = value["module"]
        folder = value["hugo_specs"]["folder_name"]
        title = value["hugo_specs"].get("title", folder.replace("-", " ").title())
        description = value["hugo_specs"].get("description", "No description available.")
        weight = value["hugo_specs"].get("weight", 0)
        content[folder] = {"title": title, "module": module, "description": description, "weight": weight}
    return content


def create_markdown_index_page(root_directory):
    """Create an _index.md file for each directory in the root directory.
    
    Skips any directory that already contains an _index.md.
    """
    page_content = build_page_content_from_source()

    for dirpath, dirnames, filenames in os.walk(root_directory):       
        
        # Handle top-most index separately (ref/python/_index.md)
        if dirpath == root_directory:
            create_python_index_file(dirpath, page_content)
            continue

        # Create _index.md for subdirectories
        dir_name = os.path.basename(dirpath)
        print(f"Creating _index.md for directory: {dir_name}")

        # Get the title, description, and module from the page_content
        title = page_content.get(dir_name, {}).get("title", dir_name.replace("-", " ").replace("_", " ").title())
        description = page_content.get(dir_name, {}).get("description", "")
        module_name = page_content.get(dir_name, {}).get("module", "")
        
        if title == "Classes":
            weight = 30
        elif title == "Functions":
            weight = 20
        else:
            weight = page_content.get(dir_name, {}).get("weight", 0)

        index_file = os.path.join(dirpath, "_index.md")
        # Check if the directory name contains "sdk" and adjust the title accordingly
        if "sdk" in dir_name:
            create_python_sdk_index_file(index_file, dir_name,  page_content)
        else:
            # For other directories, use the original title
            with open(index_file, 'w') as file:
                file.write(f"---\ntitle: {title}\n")
                file.write(f"module: {module_name}\n")
                file.write(f"weight: {weight}\n")
                file.write("---\n")
                file.write(f"{description}\n")

        print(f"Created {index_file}\n")

def create_python_sdk_index_file(filepath,dir_name, page_content):

    manual_description = """Train and fine-tune models, manage models from experimentation to production. For guides and examples, see https://docs.wandb.ai."""

    title = page_content.get(dir_name, {}).get("title", dir_name.replace("-", " ").title())
    module_name = page_content.get(dir_name, {}).get("module", "")
    weight = page_content.get(dir_name, {}).get("weight", 10) 

    with open(filepath, 'w') as file:
        file.write(f"---\ntitle: {title.upper()}\n")
        file.write(f"module: {module_name}\n")
        file.write(f"weight: {weight}\n")
        file.write("no_list: true\n")
        file.write("---\n")
        file.write(manual_description)
    return


def create_python_index_file(filepath, page_content):
    """Create an _index.md file for the top-level python folder."""

    index_file = os.path.join(filepath, "_index.md")
    title = f"Python Library v({wandb.__version__})"

    # Generate cards dynamically from page_content
    card_blocks = []
    for folder, data in page_content.items():
        if "sdk" not in data['module'] and data['title'] != "Actions":
            url = f"/ref/python/{folder}"
            card = f"""    {{{{< card >}}}}
            <a href="{url}">
            <h2 className="card-title">{data['title']}</h2></a>
            <p className="card-content">{data['description']}</p>
        
        {{{{< /card >}}}}"""
            card_blocks.append(card)
        else:
            # Skip SDK modules for the top-level index
            continue

    url = f"/ref/python/sdk"   
    manual_card = f"""    {{{{< card >}}}}
        <a href="{url}">
        <h2 className="card-title">Python Reference</h2></a>
        <p className="card-content">Train and fine-tune models, manage models from experimentation to production.</p>
    
    {{{{< /card >}}}}"""
    card_blocks.append(manual_card)

    # Split into two panes
    midpoint = (len(card_blocks) + 1) // 2
    panes = [
        "{{< cardpane >}}\n" + "\n".join(card_blocks[:midpoint]) + "\n{{< /cardpane >}}",
        "{{< cardpane >}}\n" + "\n".join(card_blocks[midpoint:]) + "\n{{< /cardpane >}}"
    ]
    cardpane = "\n".join(panes)

    with open(index_file, 'w') as file:
        file.write(f"---\ntitle: {title}\n---\n")
        file.write(f"{cardpane}\n")
    print(f"Created {index_file}\n")



def main(args):
    create_markdown_index_page(args.source_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory", default="python", help="Directory where the markdown files exist")
    args = parser.parse_args()
    main(args)
