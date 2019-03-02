#!/usr/bin/env python3
"""
Set of helpers to assist with debugging during development
"""

import json


def pretty_print(obj: dict) -> None:
    """
    Pretty-print a dictionary as a JSON object, useful for reading metadata
    while analyzing a file.
    :param obj: A dict object to pretty-print
    :return: None
    """
    print(json.dumps(obj, indent=4, sort_keys=True, separators=(',', ': ')))
