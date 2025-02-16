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

def main():
    SERIES_NAME = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SERIES_NAME

    # Initialize APT
    apt_pkg.init_system()

    # Initialize Launchpad variables
    launchpad = Launchpad.login_anonymously(
        "elementary daily test", "production", "~/.launchpadlib/cache/", version="devel"
    )

    packages_and_upstream = get_packages_list()

    for package_and_upstream in packages_and_upstream:
        package, upstream_series = package_and_upstream.split(":", 1)
        print(package, upstream_series)

if __name__ == "__main__":
    main()
