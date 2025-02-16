#!/usr/bin/env python3

import os
import subprocess
import sys
from time import sleep
import apt_pkg
from github import Github
from launchpadlib.launchpad import Launchpad

DEFAULT_SERIES_NAME = "noble"

SERIES_NAME = sys.argv[1]

if not SERIES_NAME:
    SERIES_NAME = DEFAULT_SERIES_NAME

def get_packages_list() -> list:
    with open("/tmp/patched-packages", 'r', encoding='utf-8') as file:
        items = file.read().splitlines()
    return items


print()