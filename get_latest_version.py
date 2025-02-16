#!/usr/bin/env python3

import os
import subprocess
import sys
from time import sleep
import apt_pkg
import git.config
from github import Github
from launchpadlib.launchpad import Launchpad
import git

DEFAULT_SERIES_NAME = "noble"

def get_packages_list() -> list:
    with open("/tmp/patched-packages", 'r', encoding='utf-8') as file:
        items = file.read().splitlines()
    return items

def main():
    SERIES_NAME = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SERIES_NAME

    # Configuring this repo to be able to commit as a bot
    current_repo = git.Repo('.')
    with current_repo.config_writer() as git_config:
        git_config.set_value('user', 'email', "github-actions[bot]@users.noreply.github.com")
        git_config.set_value('user', 'name', "github-actions[bot]")
        git_config.add_value('safe','directory', "/__w/os-patches/os-patches")

    # github_token = os.environ["GITHUB_TOKEN"]
    # github_repo = os.environ["GITHUB_REPOSITORY"]
    # github = Github(github_token)
    # repo = github.get_repo(github_repo)



    # Initialize APT
    apt_pkg.init_system()

    # Initialize Launchpad variables
    launchpad = Launchpad.login_anonymously(
        "elementary daily test", "production", "~/.launchpadlib/cache/", version="devel"
    )

    ubuntu = launchpad.distributions["ubuntu"]
    ubuntu_archive = ubuntu.main_archive
    patches_archive = launchpad.people["elementary-os"].getPPAByName(
        distribution=ubuntu, name="os-patches"
    )

    packages_and_upstream = get_packages_list()

    for package_and_upstream in packages_and_upstream:
        package, *upstream_series_name = package_and_upstream.split(":", 1)
        upstream_series_name = upstream_series_name[0] if upstream_series_name else SERIES_NAME
        print(package, upstream_series_name)

        series = ubuntu.getSeries(name_or_version=SERIES_NAME)
        upstream_series = ubuntu.getSeries(name_or_version=upstream_series_name)

if __name__ == "__main__":
    main()
