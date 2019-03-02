#!/usr/bin/env python3

import json


def pretty_print(obj: dict) -> None:
    print(json.dumps(obj, indent=4, sort_keys=True, separators=(',', ': ')))
