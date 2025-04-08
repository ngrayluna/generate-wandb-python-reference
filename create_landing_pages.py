#!/usr/bin/env python

import os
import argparse

from configuration import SOURCE


def build_page_content_from_source():
    """Construct page content from the SOURCE dictionary."""
    content = {}
    for value in SOURCE.values():
        folder = value["hugo_specs"]["folder_name"]
        title = value["hugo_specs"].get("title", folder.replace("-", " ").title())
        description = value["hugo_specs"].get("description", "No description available.")
        weight = value["hugo_specs"].get("weight", 0)
        content[folder] = {"title": title, "description": description, "weight": weight}
    return content


def create_markdown_index_page(root_directory):
    """Create an _index.md file for each directory in the root directory.
    
    Skips any directory that already contains an _index.md.
    """
    page_content = build_page_content_from_source()

    for dirpath, dirnames, filenames in os.walk(root_directory):
        if '_index.md' in filenames:
            continue

        # Handle top-level index separately
        if dirpath == root_directory:
            create_python_index_file(dirpath, page_content)
            continue

        dir_name = os.path.basename(dirpath)
        print(f"Creating _index.md for directory: {dir_name}")
        title = page_content.get(dir_name, {}).get("title", dir_name.replace("-", " ").title())
        description = page_content.get(dir_name, {}).get("description", "No description available.")
        weight = page_content.get(dir_name, {}).get("weight", 0)

        index_file = os.path.join(dirpath, "_index.md")
        with open(index_file, 'w') as file:
            if weight:
                file.write(f"---\ntitle: {title}\nweight: {weight}\n---\n{description}\n")
            else:
                file.write(f"---\ntitle: {title}\n---\n{description}\n")
        print(f"Created {index_file}\n")


def create_python_index_file(filepath, page_content):
    """Create an _index.md file for the top-level python-library folder."""

    index_file = os.path.join(filepath, "_index.md")
    title = "Python API Reference"

    # Generate cards dynamically from page_content
    card_blocks = []
    for folder, data in page_content.items():
        url = f"/ref/python-library/{folder}"
        card = f"""    {{{{< card >}}}}
        <a href="{url}">
        <h2 className="card-title">{data['title']}</h2>
        <p className="card-content">{data['description']}</p>
        </a>
    {{{{< /card >}}}}"""
        card_blocks.append(card)

    # Split into two panes
    midpoint = (len(card_blocks) + 1) // 2
    panes = [
        "{{< cardpane >}}\n" + "\n".join(card_blocks[:midpoint]) + "\n{{< /cardpane >}}",
        "{{< cardpane >}}\n" + "\n".join(card_blocks[midpoint:]) + "\n{{< /cardpane >}}"
    ]
    cardpane = "\n".join(panes)

    with open(index_file, 'w') as file:
        file.write(f"---\ntitle: {title}\n---\n{cardpane}")
    print(f"Created {index_file}\n")


def main(args):
    print("\nChecking for _index.md files...")
    create_markdown_index_page(args.source_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory", default="python-library", help="Directory where the markdown files exist")
    args = parser.parse_args()
    main(args)
