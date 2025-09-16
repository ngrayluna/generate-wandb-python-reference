#!/usr/bin/env python3
"""
Post-process markdown files to remove '_wandb' and everything after it from filenames.
_wandb is added by LazyDocs to avoid conflicts during generation.
Also includes function to delete empty directories.
"""

import os
from pathlib import Path
import argparse
import yaml


def extract_frontmatter(file_path):
    """
    Extract frontmatter from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Dictionary containing frontmatter data or empty dict if no frontmatter
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file starts with frontmatter delimiter
        if content.startswith('---'):
            # Find the closing delimiter
            end_index = content.find('---', 3)
            if end_index != -1:
                frontmatter_text = content[3:end_index].strip()
                return yaml.safe_load(frontmatter_text) or {}
    except Exception as e:
        print(f"Error reading frontmatter from {file_path}: {e}")

    return {}


def clean_filename(filename):
    """
    Remove '_wandb' and everything after it from a filename.

    Args:
        filename: The original filename

    Returns:
        The cleaned filename

    Examples:
        >>> clean_filename("histogram_wandb.plot.md")
        'histogram.md'
        >>> clean_filename("Api_wandb.apis.public.md")
        'Api.md'
        >>> clean_filename("regular_file.md")
        'regular_file.md'
    """
    if '_wandb' in filename:
        # Split at '_wandb' and take only the first part
        base_name = filename.split('_wandb')[0]
        # Get the file extension (should be .md)
        _, ext = os.path.splitext(filename)
        return base_name + ext
    return filename


def get_unique_filename(base_path):
    """
    Get a unique filename by appending numbers if necessary.

    Args:
        base_path: Path object for the desired filename

    Returns:
        Path object with a unique filename
    """
    if not base_path.exists():
        return base_path

    # Split the filename and extension
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent

    # Try appending numbers until we find a unique name
    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def rename_markdown_files(directory, dry_run=False):
    """
    Rename all markdown files in a directory tree by removing '_wandb' and everything after.
    Handles conflicts by checking frontmatter and either deleting duplicates or appending numbers.

    Args:
        directory: Path to the directory to process
        dry_run: If True, only print what would be renamed without actually renaming

    Returns:
        List of tuples (old_path, new_path) for renamed files
    """
    directory = Path(directory)
    renamed_files = []
    deleted_files = []

    # Find all markdown files recursively
    for md_file in directory.rglob('*.md'):
        old_name = md_file.name
        new_name = clean_filename(old_name)

        # Only rename if the filename actually changed
        if old_name != new_name:
            old_path = md_file
            new_path = md_file.parent / new_name

            if dry_run:
                if new_path.exists():
                    # Check frontmatter to determine action
                    old_frontmatter = extract_frontmatter(old_path)
                    new_frontmatter = extract_frontmatter(new_path)

                    old_namespace = old_frontmatter.get('namespace', '')
                    new_namespace = new_frontmatter.get('namespace', '')
                    old_obj_type = old_frontmatter.get('python_object_type', '')
                    new_obj_type = new_frontmatter.get('python_object_type', '')

                    if old_namespace == new_namespace and old_obj_type == new_obj_type:
                        print(f"Would delete duplicate: {old_path} (same as {new_path})")
                        deleted_files.append(str(old_path))
                    else:
                        unique_path = get_unique_filename(new_path)
                        print(f"Would rename with number: {old_path} -> {unique_path}")
                        renamed_files.append((str(old_path), str(unique_path)))
                else:
                    print(f"Would rename: {old_path} -> {new_path}")
                    renamed_files.append((str(old_path), str(new_path)))
            else:
                # Check if target file already exists
                if new_path.exists():
                    # Extract and compare frontmatter
                    old_frontmatter = extract_frontmatter(old_path)
                    new_frontmatter = extract_frontmatter(new_path)

                    old_namespace = old_frontmatter.get('namespace', '')
                    new_namespace = new_frontmatter.get('namespace', '')
                    old_obj_type = old_frontmatter.get('python_object_type', '')
                    new_obj_type = new_frontmatter.get('python_object_type', '')

                    if old_namespace == new_namespace and old_obj_type == new_obj_type:
                        # Same namespace and type - delete the file being renamed
                        print(f"Deleting duplicate: {old_path} (same as {new_path})")
                        old_path.unlink()
                        deleted_files.append(str(old_path))
                    else:
                        # Different namespace or type - append number to filename
                        unique_path = get_unique_filename(new_path)
                        old_path.rename(unique_path)
                        print(f"Renamed with number: {old_path} -> {unique_path}")
                        renamed_files.append((str(old_path), str(unique_path)))
                else:
                    old_path.rename(new_path)
                    print(f"Renamed: {old_path} -> {new_path}")
                    renamed_files.append((str(old_path), str(new_path)))

    if deleted_files:
        print(f"\nTotal files {'that would be' if dry_run else ''} deleted as duplicates: {len(deleted_files)}")

    return renamed_files


def delete_empty_directories(root_directory):
    """Delete empty directories in the root directory."""
    for dirpath, dirnames, filenames in os.walk(root_directory, topdown=False):
        if not dirnames and not filenames:
            print(f"Deleting empty directory: {dirpath}")
            os.rmdir(dirpath)


def main():
    parser = argparse.ArgumentParser(
        description='Remove "_wandb" and everything after from markdown filenames and clean up empty directories'
    )
    parser.add_argument(
        '--directory',
        default='python',
        help='Directory to process (will process all subdirectories)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be renamed without actually renaming'
    )
    parser.add_argument(
        '--skip-empty-cleanup',
        action='store_true',
        help='Skip deletion of empty directories'
    )

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist")
        return 1

    print(f"Processing directory: {args.directory}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Rename markdown files
    renamed_files = rename_markdown_files(args.directory, args.dry_run)

    print()
    print(f"Total files {'that would be' if args.dry_run else ''} renamed: {len(renamed_files)}")

    # Delete empty directories (unless skipped or in dry-run mode)
    if not args.skip_empty_cleanup and not args.dry_run:
        print("\nCleaning up empty directories...")
        delete_empty_directories(args.directory)

    return 0


if __name__ == '__main__':
    exit(main())