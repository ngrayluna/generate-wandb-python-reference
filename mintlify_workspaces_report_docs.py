#!/bin/usr/python
import os
import re
import glob
import argparse

def remove_images(markdown_text):
    """Remove all <img> tags from the markdown text."""
    img_pattern = r'<img[^>]*>'
    cleaned_text = re.sub(img_pattern, '', markdown_text).strip()
    return cleaned_text

def remove_markdownlint_disable(markdown_text):
    """Remove markdownlint-disable HTML comments from the markdown text."""
    pattern = r'<!--\s*markdownlint-disable\s*-->'
    cleaned_text = re.sub(pattern, '', markdown_text).strip()
    return cleaned_text


def remove_module_header(markdown_text):
    """Remove the module header line (e.g., '# <kbd>module</kbd> `module.name`')."""
    pattern = r'#\s*<kbd>module</kbd>\s*`[^`]*`\s*\n?'
    cleaned_text = re.sub(pattern, '', markdown_text).strip()
    return cleaned_text


def remove_internal_classes(markdown_text):
    """Remove class definitions marked as INTERNAL.

    Matches patterns like:
        ## <kbd>class</kbd> `ClassName`
        INTERNAL: This class is not for public use.
        ---

    Handles trailing whitespace and optional --- separator.
    """
    pattern = r'#{1,}\s*<kbd>class</kbd>\s*`[^`]*`\s*\nINTERNAL:[^\n]*[\s\n]*(?:---)?'
    cleaned_text = re.sub(pattern, '', markdown_text).strip()
    return cleaned_text


def remove_empty_lines(markdown_text):
    """Remove empty lines from the markdown text."""
    cleaned_text = re.sub(r'\n\s*\n', '\n', markdown_text).strip()
    return cleaned_text

def rename_markdown_file(old_filename, output_directory="."):
    """
    Rename the markdown file from old_filename to new_filename.
    """
    base_name = os.path.basename(old_filename).split('.')[1]
    os.rename(old_filename, os.path.join(output_directory, base_name + ".mdx"))

def _markdown_title(filename):
    """
    Create markdown title based on the filename read in.
    """
    base_name = os.path.basename(filename).split('.')[1].capitalize()
    return f"title: {base_name}\n"


def add_frontmatter(filename):
    """Add frontmatter to the markdown file.
    
    Args:
        filename (str): Name of the file.
    """
    return "---\n" + _markdown_title(filename) +  "---\n"


def add_github_import_statement():
    """Add GitHub import statement to the markdown file.
    
    Args:
        filename (str): Name of the file.
    """
    return "import { GitHubLink } from '/snippets/en/_includes/github-source-link.mdx';" + "\n\n"

def format_github_button(filename, base_url="https://github.com/wandb/wandb-workspaces/blob/main/wandb_workspaces/"):
    """Add GitHub button to the markdown file.
    
    Args:
        filename (str): Name of the file.
        base_url (str): Base URL for the GitHub button.
    """

    name = os.path.basename(filename).split('.')[1]
    if "reports" in name:
        version = os.path.basename(filename).split('.')[2]
        href_links = os.path.join(base_url, name + "/" + version + "/internal.py")
    else:
        href_links = os.path.join(base_url, name + "/internal.py")
    return _github_button(href_links)

def _github_button(href_links):
    """To do: Add hugo scripting to add this function. For now, just add code line # for debugging.
    
    Args:
        href_links (str): URL for the GitHub button.
    """
    return '<GitHubLink url="' + href_links + '" />' + "\n\n"


def main(args):

    # Read input markdown file
    for filename in glob.glob(os.path.join(os.getcwd(), args.markdown_directory, "*.md")):

        # Process each markdown file
        print("Processing...", filename)
        with open(filename, "r+") as file:

            # Process markdown text
            markdown_text = file.read()
            markdown_text = remove_markdownlint_disable(markdown_text)
            markdown_text = remove_module_header(markdown_text)
            markdown_text = remove_images(markdown_text)
            markdown_text = remove_internal_classes(markdown_text)
            markdown_text = remove_empty_lines(markdown_text)
            # Alphabetize headings can be added here if needed

            # Write back to the file with frontmatter and GitHub import statement
            file.seek(0)
            file.write(add_frontmatter(filename))
            file.write(add_github_import_statement())
            file.write(format_github_button(filename))
            file.write(markdown_text)
            file.truncate()

        # Rename markdown file and change extension to .mdx
        rename_markdown_file(filename, output_directory=args.markdown_directory)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add frontmatter and GitHub link to markdown files.")
    parser.add_argument("--markdown_directory", default="wandb_sdk_docs",
                        help="Directory containing markdown files to process")
    main(parser.parse_args())

# wandb_workspaces.workspaces.interface.md