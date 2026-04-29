# openLCA JSON Formatter
    # Reshapes from single- to multi-line; sorts keys and object-array elements.
    # Consistent JSON format ensures clean, readable Git diffs.
    # Adapted from pre-commit/pre-commit-hooks, pretty_format_json.py

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from difflib import unified_diff


# For object arrays (i.e., list of nested JSON), choose the object.field from which
# values act as the sort key; the first .field found on all array elements is used:
SORT_BY_FIELDS = ["internalId", "name", "@id"]
# E.g., with the above list, sorting of Process.exchanges occurs on .internalId, 
# of UnitGroup.units on .name, and any list with neither uses .@id as the fall-back

# Default sequence of keys to keep (where existent) at the top of each object:
TOP_KEYS = ["@type", "@id", "name", 'internalId']


def _get_pretty_format(
    contents: str,
    indent: int,
    top_keys: Sequence[str] = [],
    array_sort_keys: Sequence[str] = [],
) -> str:
    json_pretty = json.dumps(
        sort_json(json.loads(contents),
                  top_keys=top_keys,
                  array_sort_keys=array_sort_keys),
        indent=indent,
        ensure_ascii=False,
    )
    return f"{json_pretty}\n"


def sort_json(
    obj: object, 
    top_keys: Sequence[str] = TOP_KEYS,
    array_sort_keys: Sequence[str] = SORT_BY_FIELDS,
    # top_keys: Sequence[str] = TOP_KEYS,
    # array_sort_keys: Sequence[str] = SORT_BY_FIELDS,
) -> object:
    """
    Recursively sort JSON by keys alphabetically and object arrays by values 
    of the first-available array_sort_keys (default: SORT_BY_FIELDS) key 
    found on all elements.
    
    Args:
        obj: JSON object or component thereof {dict, list, primitive}
    Returns:
        Sorted JSON object
    """
    if isinstance(obj, dict):
        return {
            **{key: sort_json(obj[key]) for key in top_keys 
               if key in obj},
            **{key: sort_json(value) for key, value in sorted(obj.items()) 
               if key not in top_keys},
        }
    elif isinstance(obj, list):
        if (all(isinstance(item, list) for item in obj)):
            # skip nested arrays (e.g., Location.geometry.*.coordinates)
            return obj
        sorted_list = [sort_json(item) for item in obj]
        if (sorted_list and all(isinstance(item, dict) for item in sorted_list)):
            for field in array_sort_keys:
                if all(field in item for item in sorted_list):
                    sorted_list = sorted(sorted_list, key=lambda x: x[field])
                    return sorted_list
        return sorted_list
    else:
        return obj


def _autofix(filename: str, new_contents: str) -> None:
    print(f"Fixing file {filename}")
    with open(filename, "w", encoding="UTF-8") as f:
        f.write(new_contents)


def parse_keys(s: str) -> list[str]:
    return s.split(",")


def get_diff(source: str, target: str, file: str) -> str:
    source_lines = source.splitlines(True)
    target_lines = target.splitlines(True)
    diff = unified_diff(source_lines, target_lines, fromfile=file, tofile=file)
    return "".join(diff)


def main(argv: Sequence[str] | None = None) -> int:
    """
    Script for reshaping a filename meets certain requirements.
    
    Args:
        argv: The arguments passed on the command line.
    Returns:
        Exit code for the pre-commit hook, where 0 (success) allows the 
        commit to proceed and 1 (failure) stops the commit.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--array-sort-keys",
        type=parse_keys,
        default=SORT_BY_FIELDS,
        help=("Ordered list of keys on which object arrays are sorted by the "
              "first-omnipresent key's values"),
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help=("The number of indent spaces or a string to be used as delimiter"
              " for indentation level e.g. 4 or '\t' (Default: 2)"),
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        dest="preview",
        help="Preview formatting updates to not-pretty-formatted files",
    )
    parser.add_argument(
        "--top-keys",
        type=parse_keys,
        default=TOP_KEYS,
        help="Ordered list of keys to keep at the top of JSON hashes",
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to fix")
    args = parser.parse_args(argv)

    status = 0

    for json_file in args.filenames:
        with open(json_file, encoding="UTF-8") as f:
            contents = f.read()
        try:
            pretty_contents = _get_pretty_format(
                contents, 
                args.indent, 
                top_keys=args.top_keys,
                array_sort_keys=args.array_sort_keys,
            )
        except ValueError:
            print(
                f"Input File {json_file} is not a valid JSON, consider using "
                "check-json",
            )
            status = 1
        else:
            if contents != pretty_contents:
                if args.preview:
                    diff_output = get_diff(contents, pretty_contents, json_file)
                    sys.stdout.buffer.write(diff_output.encode())
                else:
                    _autofix(json_file, pretty_contents)
                status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())