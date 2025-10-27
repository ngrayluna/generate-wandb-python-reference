#!/usr/bin/env python3
"""
Check MDX file list against docs.json Python group entries.

This script validates that:
1. All MDX files in mdx_file_list.json are represented in docs.json
2. Path and naming conventions match (checks for case mismatches)
"""

import json
from typing import Dict, List, Set
from datetime import datetime

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
        print("\n⚠️  CASE/NAMING MISMATCHES:")
        print(SEPARATOR)
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


def main() -> None:
    """
    Main execution function.

    Performs validation and exits with appropriate status code:
    - 0: validation passed
    - 1: validation failed or error occurred
    """
    try:
        results = check_mdx_vs_docsjson()
        print_results(results)
        save_json_report(results)

        # Exit with error code if validation failed
        summary = results["summary"]
        if summary["mdx_only_count"] > 0 or summary["case_mismatch_count"] > 0:
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
    main()
