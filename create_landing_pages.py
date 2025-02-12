#!/bin/usr/python
import os
import glob
import argparse

# Go to each directory
# If _index.md does not exist, 
# create one + add header

# if it exists, check that the frontmatter exists

def create_landing_page(root_directory):


    # Check if the directory exists
    for dirpath, dirnames, filenames in os.walk(root_directory):
        if '_index.md' in filenames:
            print(f"'_index.md' exists in: {dirpath}")
        else:
            print(f"'_index.md' is missing in: {dirpath}")
            create_index_file(dirpath)
    return


def create_index_file(filepath):
    # Create _index.md and add header
    index_file = os.path.join(filepath, "_index.md")
    with open(index_file, 'w') as file:
        file.write("---\ntitle: " + os.path.basename(filepath) + "\n---\n")
    print(f"Created {index_file}")
    return


# def check_frontmatter(filepath):
#     return




def main(args):
    print("\nCreating landing pages for SDK docs...")    

    create_landing_page(args.source_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_directory", default="python-library", help="directory where the markdown exist")
    args = parser.parse_args()
    main(args)