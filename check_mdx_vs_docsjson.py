#!/usr/bin/env python3
"""
Check MDX file list against docs.json Python group entries.

This script validates that:
1. All MDX files in mdx_file_list.json are represented in docs.json
2. Path and naming conventions match (checks for case mismatches)
3. Optionally updates docs.json with missing pages (--update flag)
"""

import argparse
import json
import shutil
from typing import Dict, List, Set, Optional
from datetime import datetime
from pathlib import Path

# Configuration constants
DOCS_JSON_PREFIX = "models/ref/"
DEFAULT_MDX_FILE_LIST = "mdx_file_list.json"
DEFAULT_DOCS_JSON = "docs.json"
DEFAULT_OUTPUT_REPORT = "mdx_docsjson_validation_report.json"
SEPARATOR = "=" * 70
EN_LANGUAGE = "en"
PYTHON_GROUP = "Python"


def load_mdx_file_list(filepath: str = DEFAULT_MDX_FILE_LIST) -> List[str]:
    """Load the MDX file list from JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def _extract_pages_recursive(pages_list: List, accumulator: Set[str]) -> None:
    """
    Recursively extract page paths from nested structure.

    Args:
        pages_list: List of page items (strings or dicts)
        accumulator: Set to collect page paths
    """
    for item in pages_list:
        if isinstance(item, str):
            accumulator.add(item)
        elif isinstance(item, dict) and "pages" in item:
            _extract_pages_recursive(item["pages"], accumulator)


def _find_python_group(pages_list: List, accumulator: Set[str]) -> bool:
    """
    Find Python group in nested structure and extract its pages.

    Args:
        pages_list: List of page items to search
        accumulator: Set to collect Python group page paths

    Returns:
        True if Python group was found, False otherwise
    """
    for item in pages_list:
        if isinstance(item, dict):
            if item.get("group") == PYTHON_GROUP:
                _extract_pages_recursive(item.get("pages", []), accumulator)
                return True
            elif "pages" in item:
                if _find_python_group(item["pages"], accumulator):
                    return True
    return False


def extract_python_pages_from_docs(docs_json_path: str = DEFAULT_DOCS_JSON) -> Set[str]:
    """
    Extract all Python group pages from docs.json (en language only).

    Args:
        docs_json_path: Path to docs.json file

    Returns:
        Set of page paths from the Python group

    Raises:
        ValueError: If 'en' language section is not found
    """
    with open(docs_json_path, 'r', encoding='utf-8') as f:
        docs_data = json.load(f)

    # Navigate to the English language section
    languages = docs_data.get("navigation", {}).get("languages", [])
    en_data = None
    for lang_section in languages:
        if lang_section.get("language") == EN_LANGUAGE:
            en_data = lang_section
            break

    if not en_data:
        raise ValueError(f"Could not find '{EN_LANGUAGE}' language section in docs.json")

    # Find the Python group within the structure
    python_pages = set()
    tabs = en_data.get("tabs", [])
    for tab in tabs:
        if _find_python_group(tab.get("pages", []), python_pages):
            break

    return python_pages


def normalize_docsjson_path(docs_path: str) -> str:
    """
    Convert docs.json path to MDX file path format.

    Args:
        docs_path: Path from docs.json (e.g., 'models/ref/python/functions/agent')

    Returns:
        MDX file path (e.g., 'python/functions/agent.mdx')
    """
    if docs_path.startswith(DOCS_JSON_PREFIX):
        docs_path = docs_path[len(DOCS_JSON_PREFIX):]
    return f"{docs_path}.mdx"


def create_backup(filepath: str) -> str:
    """
    Create a backup of the specified file.

    Args:
        filepath: Path to file to backup

    Returns:
        Path to backup file
    """
    backup_path = f"{filepath}.backup"
    shutil.copy2(filepath, backup_path)
    print(f"📦 Creating backup: {backup_path} ✓")
    return backup_path


def path_segment_to_group_name(segment: str) -> str:
    """
    Convert a path segment to a group name.

    Args:
        segment: Path segment (e.g., 'automations', 'data-types')

    Returns:
        Group name (e.g., 'Automations', 'Data Types')
    """
    # Handle special cases
    if segment == "data-types":
        return "Data Types"
    elif segment == "custom-charts":
        return "Custom Charts"
    elif segment == "public-api":
        return "Public API"
    elif segment == "functions":
        return "Global Functions"

    # Default: capitalize first letter
    return segment.capitalize()


def mdx_path_to_group_and_page(mdx_path: str) -> tuple[Optional[str], str]:
    """
    Extract group name and page path from MDX file path.

    Args:
        mdx_path: MDX file path (e.g., 'python/automations/automation.mdx')

    Returns:
        Tuple of (group_name, docs_json_page_path)
        e.g., ('Automations', 'models/ref/python/automations/automation')
    """
    # Remove .mdx extension
    path_without_ext = mdx_path.replace(".mdx", "")

    # Split path
    parts = path_without_ext.split("/")

    # Need at least python/category/page
    if len(parts) < 3 or parts[0] != "python":
        return None, ""

    # Extract category (second segment)
    category = parts[1]
    group_name = path_segment_to_group_name(category)

    # Build docs.json path with prefix
    docs_json_path = f"{DOCS_JSON_PREFIX}{path_without_ext}"

    return group_name, docs_json_path


def find_and_update_group(pages_list: List, target_group: str, new_page: str) -> bool:
    """
    Find a group in nested structure and insert page alphabetically.

    Args:
        pages_list: List of page items to search
        target_group: Group name to find (e.g., 'Automations')
        new_page: Page path to insert (e.g., 'models/ref/python/automations/newpage')

    Returns:
        True if group was found and page added, False otherwise
    """
    for item in pages_list:
        if isinstance(item, dict):
            if item.get("group") == target_group:
                # Found the target group
                group_pages = item.get("pages", [])

                # Check if page already exists (case-insensitive)
                new_page_lower = new_page.lower()
                for page in group_pages:
                    if isinstance(page, str) and page.lower() == new_page_lower:
                        # Page already exists, skip insertion
                        return False

                # Insert alphabetically (case-insensitive sort)
                insert_index = 0

                for i, page in enumerate(group_pages):
                    # Only compare with string pages (not nested groups)
                    if isinstance(page, str):
                        if page.lower() > new_page_lower:
                            break
                        insert_index = i + 1
                    else:
                        # For nested groups, consider them as coming after all landing pages
                        insert_index = i + 1

                group_pages.insert(insert_index, new_page)
                return True
            elif "pages" in item:
                # Recursively search nested groups
                if find_and_update_group(item["pages"], target_group, new_page):
                    return True

    return False


def update_docs_json_with_missing_pages(
    missing_mdx_files: List[str],
    docs_json_path: str = DEFAULT_DOCS_JSON
) -> Dict[str, List[str]]:
    """
    Update docs.json with missing MDX pages.

    Args:
        missing_mdx_files: List of MDX files not in docs.json
        docs_json_path: Path to docs.json file

    Returns:
        Dictionary mapping group names to lists of added pages
    """
    if not missing_mdx_files:
        print("\n✓ No pages to add to docs.json")
        return {}

    # Create backup
    create_backup(docs_json_path)

    # Load docs.json
    with open(docs_json_path, 'r', encoding='utf-8') as f:
        docs_data = json.load(f)

    # Track additions by group
    additions = {}

    print(f"\n📝 Processing {len(missing_mdx_files)} missing page(s)...\n")

    # Find English language section
    languages = docs_data.get("navigation", {}).get("languages", [])
    en_data = None
    for lang_section in languages:
        if lang_section.get("language") == EN_LANGUAGE:
            en_data = lang_section
            break

    if not en_data:
        print("❌ Error: Could not find 'en' language section in docs.json")
        return additions

    # Process each missing file
    for mdx_file in missing_mdx_files:
        group_name, docs_json_page = mdx_path_to_group_and_page(mdx_file)

        if not group_name:
            print(f"⚠️  Skipping {mdx_file}: Could not determine group")
            continue

        print(f"  {group_name}: {mdx_file}")

        # Try to add to the group
        added = False
        tabs = en_data.get("tabs", [])
        for tab in tabs:
            if find_and_update_group(tab.get("pages", []), group_name, docs_json_page):
                added = True
                break

        if added:
            if group_name not in additions:
                additions[group_name] = []
            additions[group_name].append(docs_json_page)
        else:
            print(f"    ⚠️  Warning: Could not find '{group_name}' group in docs.json")

    # Save updated docs.json
    if additions:
        with open(docs_json_path, 'w', encoding='utf-8') as f:
            json.dump(docs_data, f, indent=2)

        print(f"\n✅ Updated docs.json with {sum(len(pages) for pages in additions.values())} new page(s)")
        print(f"\nPages added by group:")
        for group_name, pages in sorted(additions.items()):
            print(f"  {group_name}: {len(pages)} page(s)")

    return additions


def check_mdx_vs_docsjson() -> Dict:
    """
    Main validation function comparing MDX files against docs.json entries.

    Returns:
        Dictionary containing validation results with counts and detailed lists
    """
    print("Loading MDX file list...")
    mdx_files = load_mdx_file_list()

    print("Parsing docs.json for Python group entries...")
    docs_pages = extract_python_pages_from_docs()

    # Convert docs.json pages to MDX path format
    docs_as_mdx = {normalize_docsjson_path(page) for page in docs_pages}

    print(f"\nFound {len(mdx_files)} files in MDX list")
    print(f"Found {len(docs_as_mdx)} pages in docs.json Python group")
    print(f"\n{SEPARATOR}")

    # Create normalized lookup dictionaries for case-insensitive comparison
    mdx_normalized = {f.lower(): f for f in mdx_files}
    docs_normalized = {f.lower(): f for f in docs_as_mdx}

    # Check 1: MDX files not in docs.json (case-insensitive)
    mdx_only = sorted([
        mdx_file for mdx_file in mdx_files
        if mdx_file.lower() not in docs_normalized
    ])

    # Check 2: Case/naming mismatches (files exist but with different casing)
    case_mismatches = sorted([
        {"mdx_path": mdx_file, "docs_path": docs_normalized[mdx_file.lower()]}
        for mdx_file in mdx_files
        if mdx_file.lower() in docs_normalized and mdx_file != docs_normalized[mdx_file.lower()]
    ], key=lambda x: x["mdx_path"])

    # Check 3: Docs.json entries not in MDX list (informational)
    docs_only = sorted([
        docs_file for docs_file in docs_as_mdx
        if docs_file.lower() not in mdx_normalized
    ])

    # Prepare results
    results = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "mdx_file_count": len(mdx_files),
            "docsjson_page_count": len(docs_as_mdx),
            "mdx_only_count": len(mdx_only),
            "case_mismatch_count": len(case_mismatches),
            "docs_only_count": len(docs_only)
        },
        "mdx_files_not_in_docsjson": mdx_only,
        "case_naming_mismatches": case_mismatches,
        "docsjson_entries_not_in_mdx": docs_only
    }

    return results


def print_results(results: Dict) -> None:
    """
    Print validation results to console in a readable format.

    Args:
        results: Dictionary containing validation results
    """
    summary = results["summary"]

    print("\n📊 VALIDATION SUMMARY")
    print(SEPARATOR)
    print(f"MDX files in list:              {summary['mdx_file_count']}")
    print(f"Docs.json Python pages:         {summary['docsjson_page_count']}")
    print(f"MDX files not in docs.json:     {summary['mdx_only_count']}")
    print(f"Case/naming mismatches:         {summary['case_mismatch_count']}")
    print(f"Docs.json entries not in MDX:   {summary['docs_only_count']} (informational)")

    # Print MDX files not in docs.json
    if results["mdx_files_not_in_docsjson"]:
        print("\n❌ MDX FILES NOT IN DOCS.JSON:")
        print(SEPARATOR)
        for mdx_file in results["mdx_files_not_in_docsjson"]:
            print(f"  - {mdx_file}")

    # Print case mismatches
    if results["case_naming_mismatches"]:
        print("\n⚠️  CASE/NAMING MISMATCHES (not auto-fixed):")
        print(SEPARATOR)
        print("These pages exist in both locations but with different casing.")
        print("Manual review recommended.\n")
        for mismatch in results["case_naming_mismatches"]:
            print(f"  MDX:  {mismatch['mdx_path']}")
            print(f"  Docs: {mismatch['docs_path']}")
            print()

    # Print docs.json entries not in MDX (informational)
    if results["docsjson_entries_not_in_mdx"]:
        print("\nℹ️  DOCS.JSON ENTRIES NOT IN MDX LIST (informational):")
        print(SEPARATOR)
        for docs_file in results["docsjson_entries_not_in_mdx"]:
            print(f"  - {docs_file}")

    # Final status
    print(f"\n{SEPARATOR}")
    if summary['mdx_only_count'] == 0 and summary['case_mismatch_count'] == 0:
        print("✅ VALIDATION PASSED: All checks successful!")
    else:
        print("❌ VALIDATION FAILED: Issues found (see above)")
    print(SEPARATOR)


def save_json_report(results: Dict, output_path: str = DEFAULT_OUTPUT_REPORT) -> None:
    """
    Save validation results to a JSON file.

    Args:
        results: Dictionary containing validation results
        output_path: Path where JSON report will be saved
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 JSON report saved to: {output_path}")


def main(args) -> None:
    """
    Main execution function.

    Performs validation and optionally updates docs.json.
    Exits with appropriate status code:
    - 0: validation passed or pages were added
    - 1: validation failed or error occurred
    """
    try:

        results = check_mdx_vs_docsjson()
        print_results(results)
        save_json_report(results)

        summary = results["summary"]
        mdx_only = results["mdx_files_not_in_docsjson"]

        # Update docs.json if requested and there are missing pages
        if args.update and mdx_only:
            print(f"\n{SEPARATOR}")
            print("🔄 UPDATING DOCS.JSON")
            print(SEPARATOR)
            additions = update_docs_json_with_missing_pages(mdx_only)

            if additions:
                print(f"\n{SEPARATOR}")
                print("✅ Update complete! Re-run script to verify.")
                print(SEPARATOR)
        elif not args.update and mdx_only:
            print(f"\n💡 Tip: Run with --update to automatically add missing pages to docs.json")

        # Exit with error code if validation issues remain
        # (case mismatches still count as issues since they're not auto-fixed)
        if summary["case_mismatch_count"] > 0:
            exit(1)

    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON - {e}")
        exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true", default=True, help="Only generate report, don't update docs.json")
    args = parser.parse_args()
    main(args)
